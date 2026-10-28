
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

ANDROID_VOICE = False
PythonActivity = None
Intent = None
RecognizerIntent = None

if platform == "android":
    try:
        from jnius import autoclass
        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )
        Intent = autoclass("android.content.Intent")
        RecognizerIntent = autoclass(
            "android.speech.RecognizerIntent"
        )
        ANDROID_VOICE = True
    except Exception:
        pass

try:
    LabelBase.register(
        name="MarathiFont",
        fn_regular="NotoSansDevanagari.ttf"
    )
    FONT = "MarathiFont"
except Exception:
    FONT = "Roboto"

Window.clearcolor = (0.035, 0.055, 0.10, 1)


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Assistant"

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        root.add_widget(Label(
            text="🛡️ सुरक्षा सहाय्यक",
            font_name=FONT,
            font_size=dp(25),
            bold=True,
            color=(0.25, 0.85, 1, 1),
            size_hint_y=None,
            height=dp(48)
        ))

        root.add_widget(Label(
            text="तुमची डिजिटल सुरक्षा, तुमच्या हातात",
            font_name=FONT,
            font_size=dp(14),
            color=(0.8, 0.9, 1, 1),
            size_hint_y=None,
            height=dp(28)
        ))

        self.status = Label(
            text="● ॲप सुरू आहे",
            font_name=FONT,
            font_size=dp(14),
            color=(0.3, 1, 0.6, 1),
            size_hint_y=None,
            height=dp(28)
        )
        root.add_widget(self.status)

        grid = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        items = [
            ("आवाजाने कमांड", self.start_voice, (0.05, 0.40, 0.60, 1)),
            ("सुरक्षा सूचना", self.show_security, (0.12, 0.30, 0.48, 1)),
            ("बॅटरी माहिती", self.show_battery, (0.12, 0.38, 0.30, 1)),
            ("तारीख आणि वेळ", self.show_time, (0.32, 0.24, 0.48, 1)),
            ("ॲपची स्थिती", self.show_status, (0.25, 0.32, 0.43, 1)),
            ("मदत", self.show_help, (0.38, 0.28, 0.15, 1))
        ]

        for text, callback, color in items:
            button = Button(
                text=text,
                font_name=FONT,
                font_size=dp(14),
                size_hint_y=None,
                height=dp(65),
                background_normal="",
                background_color=color
            )
            button.bind(on_release=callback)
            grid.add_widget(button)

        root.add_widget(grid)

        root.add_widget(Label(
            text="कमांड लिहा किंवा आवाजाने बोला",
            font_name=FONT,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(28)
        ))

        self.command = TextInput(
            hint_text="नमस्कार / सुरक्षा / वेळ / मदत",
            font_name=FONT,
            font_size=dp(16),
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )
        self.command.bind(on_text_validate=self.run_command)
        root.add_widget(self.command)

        run_button = Button(
            text="कमांड चालवा",
            font_name=FONT,
            font_size=dp(16),
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=(0.05, 0.52, 0.72, 1)
        )
        run_button.bind(on_release=self.run_command)
        root.add_widget(run_button)

        scroll = ScrollView(
            do_scroll_x=False,
            size_hint=(1, 1)
        )

        self.output = Label(
            text="नमस्कार! मी तुमचा Security Assistant आहे.",
            font_name=FONT,
            font_size=dp(15),
            halign="left",
            valign="top",
            size_hint_y=None
        )
        self.output.bind(
            width=self.set_output_width,
            texture_size=self.set_output_height
        )
        scroll.add_widget(self.output)
        root.add_widget(scroll)

        root.add_widget(Label(
            text="सुरक्षित रहा • विचारपूर्वक इंटरनेट वापरा",
            font_name=FONT,
            font_size=dp(11),
            size_hint_y=None,
            height=dp(22),
            color=(0.6, 0.72, 0.85, 1)
        ))

        if ANDROID_VOICE:
            try:
                PythonActivity.mActivity.bind(
                    on_activity_result=self.on_voice_result
                )
            except Exception:
                pass

        return root

    def set_output_width(self, obj, width):
        obj.text_size = (width - dp(12), None)

    def set_output_height(self, obj, size):
        obj.height = size[1] + dp(20)

    def run_command(self, instance):
        command = self.command.text.strip().lower()

        if not command:
            self.output.text = "कृपया कमांड लिहा किंवा आवाजाने बोला."
            return

        if command in ("hello", "hi", "namaskar", "नमस्कार", "नमस्ते"):
            message = "नमस्कार! मी तुमचा Security Assistant आहे."
        elif command in ("status", "स्थिती", "ॲपची स्थिती"):
            message = "ॲप व्यवस्थित सुरू आहे."
        elif command in ("security", "सुरक्षा", "सुरक्षा सूचना"):
            message = self.security_text()
        elif command in ("time", "वेळ", "तारीख", "date"):
            message = self.time_text()
        elif command in ("battery", "बॅटरी"):
            message = self.battery_text()
        elif command in ("help", "मदत", "सहाय्य"):
            message = self.help_text()
        elif command in ("voice", "आवाज", "बोला"):
            self.start_voice(None)
            return
        elif command in ("clear", "पुसा", "साफ"):
            self.command.text = ""
            message = "कमांड बॉक्स साफ झाला."
        else:
            message = "ही कमांड ओळखता आली नाही. 'मदत' दाबा."

        self.output.text = message

    def security_text(self):
        return (
            "सुरक्षा सूचना\n\n"
            "१. अनोळखी लिंक उघडू नका.\n"
            "२. OTP, PIN किंवा पासवर्ड कोणालाही सांगू नका.\n"
            "३. ॲप्स विश्वासार्ह स्रोतांतून इन्स्टॉल करा.\n"
            "४. ॲपच्या परवानग्या तपासा.\n"
            "५. फोन आणि ॲप्स अपडेट ठेवा.\n"
            "६. प्रत्येक खात्यासाठी वेगळा मजबूत पासवर्ड वापरा.\n\n"
            "ही सूचना आहे; प्रत्यक्ष फोन तपासणी नाही."
        )

    def show_security(self, instance):
        self.output.text = self.security_text()

    def time_text(self):
        now = datetime.now()
        return "तारीख: " + now.strftime("%d-%m-%Y") + "\nवेळ: " + now.strftime("%I:%M:%S %p")

    def show_time(self, instance):
        self.output.text = self.time_text()

    def battery_text(self):
        try:
            from plyer import battery
            info = battery.get_state()
            percentage = info.get("percentage")
            if percentage is not None:
                return f"बॅटरी: {percentage}%"
        except Exception:
            pass
        return "बॅटरीची माहिती मिळाली नाही. फोनच्या Settings मध्ये तपासा."

    def show_battery(self, instance):
        self.output.text = self.battery_text()

    def show_status(self, instance):
        self.output.text = (
            "ॲपची स्थिती\n\n"
            "Security Assistant सुरू आहे.\n"
            "मराठी कमांड उपलब्ध आहेत.\n"
            "आवाजाची सुविधा Android Speech Recognition वर अवलंबून आहे."
        )

    def help_text(self):
        return (
            "उपलब्ध कमांड\n\n"
            "नमस्कार — अभिवादन\n"
            "स्थिती — ॲपची स्थिती\n"
            "सुरक्षा — सुरक्षा सूचना\n"
            "वेळ — तारीख आणि वेळ\n"
            "बॅटरी — बॅटरीची माहिती\n"
            "आवाज — आवाजाने कमांड\n"
            "मदत — कमांडची यादी\n"
            "पुसा — कमांड बॉक्स साफ करा"
        )

    def show_help(self, instance):
        self.output.text = self.help_text()

    def start_voice(self, instance):
        if not ANDROID_VOICE:
            self.output.text = "आवाजाची सुविधा उपलब्ध नाही. APK मध्ये तपासणे आवश्यक आहे."
            return

        try:
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "mr-IN")
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE,
                "mr-IN"
            )
            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                "कृपया मराठीत कमांड बोला"
            )
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)

            PythonActivity.mActivity.startActivityForResult(intent, 1234)
            self.output.text = "कृपया बोला..."
        except Exception as error:
            self.output.text = "आवाज सुरू करता आला नाही.\n" + str(error)

    def on_voice_result(self, request_code, result_code, intent):
        if request_code != 1234:
            return

        if result_code == -1 and intent is not None:
            try:
                results = intent.getStringArrayListExtra(
                    RecognizerIntent.EXTRA_RESULTS
                )
                if results is not None and results.size() > 0:
                    spoken = str(results.get(0))
                    self.command.text = spoken
                    self.output.text = "तुम्ही म्हटले: " + spoken
                    Clock.schedule_once(
                        lambda dt: self.run_command(None), 0.5
                    )
                else:
                    self.output.text = "आवाज समजला नाही. पुन्हा प्रयत्न करा."
            except Exception:
                self.output.text = "आवाजाचा निकाल वाचता आला नाही."
        else:
            self.output.text = "आवाज ओळखणे रद्द झाले. पुन्हा प्रयत्न करा."


if __name__ == "__main__":
    SecurityAssistantApp().run()
