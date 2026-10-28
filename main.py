
import os
import socket

from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

try:
    from plyer import battery
except Exception:
    battery = None

# Android Voice Recognition
try:
    from android import activity
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
    activity = None
    ANDROID_VOICE = False

FONT = "Roboto"
font_path = os.path.join(
    os.path.dirname(__file__),
    "NotoSansDevanagari.ttf"
)

if os.path.exists(font_path):
    try:
        LabelBase.register(
            name="MarathiFont",
            fn_regular=font_path
        )
        FONT = "MarathiFont"
    except Exception:
        pass

Window.clearcolor = (0.055, 0.075, 0.12, 1)


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Assistant"

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        scroll = ScrollView(do_scroll_x=False)

        page = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[dp(4), dp(8)]
        )
        page.bind(minimum_height=page.setter("height"))

        page.add_widget(Label(
            text="🛡️ सुरक्षा सहाय्यक",
            font_name=FONT,
            font_size=dp(27),
            bold=True,
            color=(0.25, 0.75, 1, 1),
            size_hint_y=None,
            height=dp(55)
        ))

        page.add_widget(Label(
            text="तुमचा Smart Security Dashboard",
            font_name=FONT,
            font_size=dp(15),
            color=(0.85, 0.9, 1, 1),
            size_hint_y=None,
            height=dp(35)
        ))

        self.output = Label(
            text=(
                "नमस्कार!\n\n"
                "मी तुमचा Security Assistant आहे.\n"
                "खालील Smart Tools वापरून पाहा."
            ),
            font_name=FONT,
            font_size=dp(16),
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(175)
        )
        self.output.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", (val[0] - dp(20), None))
        )
        self.output.bind(
            texture_size=lambda obj, val:
            setattr(obj, "height", max(dp(175), val[1] + dp(30)))
        )
        page.add_widget(self.output)

        self.command = TextInput(
            hint_text="कमांड लिहा: help, status, security",
            font_name=FONT,
            font_size=dp(15),
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(10), dp(12)]
        )
        self.command.bind(on_text_validate=self.run_command)
        page.add_widget(self.command)

        page.add_widget(self.make_button(
            "कमांड चालवा",
            (0.05, 0.48, 0.78, 1),
            self.run_command
        ))

        grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(260)
        )

        buttons = [
            ("🛡️ सुरक्षा", (0.08, 0.52, 0.36, 1), self.show_security),
            ("📊 स्थिती", (0.12, 0.38, 0.56, 1), self.show_status),
            ("🔋 Battery Info", (0.12, 0.45, 0.30, 1), self.show_battery),
            ("🌐 Network Info", (0.05, 0.48, 0.65, 1), self.show_network),
            ("📘 मदत", (0.34, 0.32, 0.55, 1), self.show_help),
            ("🎙️ Voice", (0.40, 0.30, 0.65, 1), self.show_voice_info),
        ]

        for text, color, callback in buttons:
            grid.add_widget(self.make_button(text, color, callback))

        page.add_widget(grid)

        page.add_widget(Label(
            text="सुरक्षित रहा • विचारपूर्वक इंटरनेट वापरा",
            font_name=FONT,
            font_size=dp(11),
            color=(0.65, 0.75, 0.85, 1),
            size_hint_y=None,
            height=dp(32)
        ))

        scroll.add_widget(page)
        root.add_widget(scroll)

        # Android speech recognition result callback
        if ANDROID_VOICE:
            try:
                activity.bind(on_activity_result=self.on_voice_result)
            except Exception:
                pass

        return root

    def make_button(self, text, color, callback):
        button = Button(
            text=text,
            font_name=FONT,
            font_size=dp(15),
            bold=True,
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=color,
            size_hint_y=None,
            height=dp(50)
        )
        button.bind(on_release=callback)
        return button

    def run_command(self, instance):
        command = self.command.text.strip().lower()

        if command in ("hello", "hi", "namaskar", "नमस्कार", "नमस्ते"):
            self.output.text = (
                "नमस्कार!\n\n"
                "मी तुमचा Security Assistant आहे."
            )
        elif command in ("status", "स्थिती"):
            self.show_status(instance)
        elif command in ("security", "सुरक्षा"):
            self.show_security(instance)
        elif command in ("battery", "बॅटरी"):
            self.show_battery(instance)
        elif command in ("network", "नेटवर्क", "internet", "इंटरनेट"):
            self.show_network(instance)
        elif command in ("help", "मदत"):
            self.show_help(instance)
        elif command in ("voice", "आवाज"):
            self.show_voice_info(instance)
        elif command in ("exit", "बंद करा"):
            self.output.text = "ॲप बंद करण्यासाठी Android चे Back बटण वापरा."
        elif command == "":
            self.output.text = "कृपया आधी कमांड लिहा."
        else:
            self.output.text = (
                "ही कमांड समजली नाही.\n\n"
                "उपलब्ध कमांड:\n"
                "hello, status, security,\n"
                "battery, network, voice, help"
            )

        self.command.text = ""

    def show_status(self, instance):
        self.output.text = (
            "📊 ॲपची स्थिती\n\n"
            "ॲप सुरू आहे.\n"
            "Smart Dashboard उपलब्ध आहे.\n"
            "बॅटरी आणि नेटवर्क टूल्स उपलब्ध आहेत.\n\n"
            "टीप: हे संपूर्ण फोन सुरक्षा स्कॅन नाही."
        )

    def show_security(self, instance):
        self.output.text = (
            "🛡️ सुरक्षा सूचना\n\n"
            "१. OTP आणि PIN गुप्त ठेवा.\n"
            "२. मजबूत पासवर्ड वापरा.\n"
            "३. अनोळखी लिंक उघडू नका.\n"
            "४. फोन आणि ॲप्स अपडेट ठेवा.\n"
            "५. दोन-स्तरीय सुरक्षा सुरू करा.\n"
            "६. संशयास्पद ॲप्स टाळा.\n"
            "७. महत्त्वाच्या फाइल्सचा बॅकअप ठेवा."
        )

    def show_battery(self, instance):
        if battery is None:
            self.output.text = "🔋 बॅटरी माहिती मिळत नाही."
            return

        try:
            info = battery.status
            if not info:
                self.output.text = "🔋 बॅटरी माहिती उपलब्ध नाही."
                return

            level = info.get("percentage", "माहिती उपलब्ध नाही")
            charging = info.get("isCharging", False)
            state = "चार्जिंग सुरू आहे" if charging else "चार्जिंग सुरू नाही"
            level_text = (
                f"{level}%" if isinstance(level, (int, float)) else str(level)
            )

            self.output.text = (
                "🔋 Battery Info\n\n"
                f"बॅटरी: {level_text}\n"
                f"स्थिती: {state}"
            )
        except Exception:
            self.output.text = "🔋 बॅटरीची माहिती मिळू शकली नाही."

    def show_network(self, instance):
        self.output.text = "🌐 इंटरनेट कनेक्शन तपासत आहे..."

        try:
            connection = socket.create_connection(
                ("1.1.1.1", 53), timeout=3
            )
            connection.close()
            self.output.text = (
                "🌐 Network Info\n\n"
                "इंटरनेट कनेक्शन उपलब्ध दिसत आहे.\n\n"
                "टीप: ही फक्त प्राथमिक कनेक्शन चाचणी आहे."
            )
        except Exception:
            self.output.text = (
                "🌐 इंटरनेट कनेक्शन तपासता आले नाही.\n\n"
                "मोबाइल डेटा किंवा Wi-Fi तपासा."
            )

    def show_help(self, instance):
        self.output.text = (
            "📘 उपलब्ध कमांड\n\n"
            "hello - नमस्कार\n"
            "status - ॲपची स्थिती\n"
            "security - सुरक्षा सूचना\n"
            "battery - बॅटरी माहिती\n"
            "network - इंटरनेट तपासणी\n"
            "voice - आवाजाने कमांड\n"
            "help - मदत\n\n"
            "कमांड लिहा किंवा Voice बटण दाबा."
        )

    def show_voice_info(self, instance):
        if not ANDROID_VOICE:
            self.output.text = (
                "🎙️ Voice Recognition उपलब्ध नाही.\n\n"
                "कृपया Android APK मध्ये वापरा."
            )
            return

        try:
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                "कृपया कमांड बोला"
            )
            # फोनच्या डिफॉल्ट भाषेतील ओळख वापरा
            PythonActivity.mActivity.startActivityForResult(intent, 1234)
            self.output.text = "🎙️ कृपया बोला..."
        except Exception:
            self.output.text = (
                "Voice सुरू करता आले नाही.\n\n"
                "फोनमध्ये Speech Recognition सेवा तपासा."
            )

    def on_voice_result(self, request_code, result_code, intent):
        if request_code != 1234:
            return

        if result_code == -1 and intent is not None:
            try:
                results = intent.getStringArrayListExtra(
                    RecognizerIntent.EXTRA_RESULTS
                )
                if results is not None and results.size() > 0:
                    spoken_text = str(results.get(0))
                    self.output.text = f"🎙️ तुम्ही म्हटले: {spoken_text}"
                    self.command.text = spoken_text
                    self.run_command(None)
                else:
                    self.output.text = "आवाज समजला नाही. पुन्हा प्रयत्न करा."
            except Exception:
                self.output.text = "आवाज वाचता आला नाही. पुन्हा प्रयत्न करा."
        else:
            self.output.text = "Voice रद्द झाला. पुन्हा प्रयत्न करा."


if __name__ == "__main__":
    SecurityAssistantApp().run()
