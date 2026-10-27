
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Assistant"
        Window.clearcolor = (0.06, 0.09, 0.15, 1)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12
        )

        layout.add_widget(Label(
            text="Security Assistant",
            font_size="24sp",
            size_hint_y=None,
            height=60
        ))

        self.output = Label(
            text="नमस्कार! मी तुमचा Security Assistant आहे.",
            font_size="18sp"
        )
        layout.add_widget(self.output)

        self.command_input = TextInput(
            hint_text="कमांड लिहा...",
            multiline=False,
            size_hint_y=None,
            height=55
        )
        layout.add_widget(self.command_input)

        run_button = Button(
            text="कमांड चालवा",
            size_hint_y=None,
            height=55
        )
        run_button.bind(on_press=self.run_command)
        layout.add_widget(run_button)

        mic_button = Button(
            text="Mic - आवाजाने बोला",
            size_hint_y=None,
            height=55
        )
        mic_button.bind(on_press=self.listen)
        layout.add_widget(mic_button)

        help_button = Button(
            text="मदत",
            size_hint_y=None,
            height=50
        )
        help_button.bind(on_press=self.show_help)
        layout.add_widget(help_button)

        return layout

    def run_command(self, instance):
        command = self.command_input.text.strip().lower()

        if command in ("hello", "hi", "namaskar", "नमस्कार"):
            response = "नमस्कार! मी तुमची मदत करायला तयार आहे."

        elif command in ("status", "stithi", "स्थिती"):
            response = "Security Assistant सुरू आहे."

        elif command in ("security", "suraksha", "सुरक्षा"):
            response = (
                "सुरक्षा सूचना: अनोळखी लिंक उघडू नका. "
                "OTP आणि पासवर्ड कोणालाही सांगू नका."
            )

        elif command in ("help", "madat", "मदत"):
            response = "hello, status, security, help या कमांड वापरा."

        else:
            response = "कमांड समजली नाही. मदत बटण दाबा."

        self.output.text = response
        self.command_input.text = ""

    def listen(self, instance):
        try:
            from android.permissions import (
                request_permissions, Permission
            )

            self.output.text = "मायक्रोफोनची परवानगी तपासत आहे..."

            request_permissions(
                [Permission.RECORD_AUDIO],
                self.on_permission_result
            )

        except Exception as error:
            self.output.text = "आवाज सुविधा उपलब्ध नाही."
            print(error)

    def on_permission_result(self, permissions, grants):
        if not grants or not grants[0]:
            self.output.text = "मायक्रोफोनची परवानगी द्या."
            return

        Clock.schedule_once(self.start_speech, 0.5)

    def start_speech(self, dt):
        try:
            from jnius import autoclass, PythonJavaClass, java_method

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )
            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass(
                "android.speech.RecognizerIntent"
            )

            class ResultListener(PythonJavaClass):
                __javainterfaces__ = [
                    "org/kivy/android/PythonActivity$ActivityResultListener"
                ]
                __javacontext__ = "app"

                @java_method("(IILandroid/content/Intent;)V")
                def onActivityResult(
                    listener_self, request_code, result_code, data
                ):
                    if request_code == 734 and result_code == -1:
                        if data is not None:
                            results = data.getStringArrayListExtra(
                                RecognizerIntent.EXTRA_RESULTS
                            )
                            if results is not None and results.size() > 0:
                                spoken = str(results.get(0))
                                Clock.schedule_once(
                                    lambda dt: self.use_voice(spoken), 0
                                )

            if not hasattr(self, "voice_listener"):
                self.voice_listener = ResultListener()
                PythonActivity.mActivityResultListeners.add(
                    self.voice_listener
                )

            intent = Intent(
                RecognizerIntent.ACTION_RECOGNIZE_SPEECH
            )
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE, "mr-IN"
            )
            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                "तुमची कमांड बोला"
            )

            activity = PythonActivity.mActivity
            activity.startActivityForResult(intent, 734)
            self.output.text = "आवाज ऐकण्यासाठी बोला..."

        except Exception as error:
            self.output.text = "आवाज सुरू झाला नाही. Build तपासा."
            print(error)

    def use_voice(self, spoken):
        self.command_input.text = spoken
        self.run_command(None)

    def show_help(self, instance):
        self.output.text = (
            "कमांड: hello, status, security, help. "
            "Mic बटणाने बोलूनही कमांड देऊ शकता."
        )


if __name__ == "__main__":
    SecurityAssistantApp().run()
