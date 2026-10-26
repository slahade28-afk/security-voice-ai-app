
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import platform

class SecurityAssistantApp(App):
    def build(self):
        self.title = "Security Voice Command AI"
        Window.clearcolor = (0.06, 0.09, 0.15, 1)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        layout.add_widget(Label(
            text="SECURITY AI ASSISTANT",
            font_size="22sp",
            size_hint_y=None,
            height=60
        ))

        self.output = Label(
            text="Namaskar! Mi tumcha Security Assistant aahe."
        )
        layout.add_widget(self.output)

        self.command_input = TextInput(
            hint_text="Command type kara...",
            multiline=False,
            size_hint_y=None,
            height=55
        )
        layout.add_widget(self.command_input)

        layout.add_widget(self.make_button(
            "Run Command", self.run_command
        ))
        layout.add_widget(self.make_button(
            "Voice Command 🎤", self.listen
        ))
        layout.add_widget(self.make_button(
            "Help", self.show_help
        ))

        if platform == "android":
            try:
                from android import activity
                activity.bind(
                    on_activity_result=self.on_activity_result
                )
            except Exception:
                pass

        return layout

    def make_button(self, title, callback):
        button = Button(
            text=title,
            size_hint_y=None,
            height=55
        )
        button.bind(on_press=callback)
        return button

    def listen(self, instance):
        if platform != "android":
            self.output.text = "Voice command Android var vapra."
            return

        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )
            Intent = autoclass("android.content.Intent")

            intent = Intent(
                "android.speech.action.RECOGNIZE_SPEECH"
            )
            intent.putExtra(
                "android.speech.extra.LANGUAGE_MODEL",
                "free_form"
            )
            intent.putExtra(
                "android.speech.extra.LANGUAGE",
                "mr-IN"
            )
            intent.putExtra(
                "android.speech.extra.PROMPT",
                "Tumchi command bola"
            )

            self.request_code = 731
            PythonActivity.mActivity.startActivityForResult(
                intent, self.request_code
            )
            self.output.text = "Aiktoy... Krupaya bola."

        except Exception as error:
            self.output.text = "Voice suru zala nahi: " + str(error)

    def on_activity_result(
        self, request_code, result_code, intent
    ):
        if request_code != 731 or intent is None:
            return

        try:
            from jnius import autoclass

            Activity = autoclass("android.app.Activity")
            if result_code != Activity.RESULT_OK:
                self.output.text = "Voice command radd zala."
                return

            results = intent.getStringArrayListExtra(
                "android.speech.extra.RESULTS"
            )

            if results and results.size() > 0:
                command = str(results.get(0))
                self.command_input.text = command
                self.process_command(command)

        except Exception:
            self.output.text = "Voice result vachata ala nahi."

    def run_command(self, instance):
        self.process_command(self.command_input.text)

    def process_command(self, text):
        command = text.strip().lower()

        if command in ("hello", "hi", "namaskar"):
            response = "Namaskar! Mi tumchi madat karayla tayar aahe."
        elif command in ("help", "madat"):
            response = "Commands: hello, status, security, help"
        elif command in ("status", "stithi"):
            response = "Security Assistant chalu aahe."
        elif command in ("security", "suraksha"):
            response = "Anolakhi links ughadu naka. OTP ani password konalahi sangu naka."
        else:
            response = "Command samajli nahi. Help vaprun paha."

        self.output.text = response
        self.speak(response)

    def speak(self, message):
        if platform == "android":
            try:
                from plyer import tts
                tts.speak(message)
            except Exception:
                self.output.text = message + " (Voice reply suru zala nahi.)"

    def show_help(self, instance):
        message = "Try kara: hello, status, security, help"
        self.output.text = message
        self.speak(message)

if __name__ == "__main__":
    SecurityAssistantApp().run()

