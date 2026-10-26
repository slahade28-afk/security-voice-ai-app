
from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
import os

FONT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "NotoSansDevanagari.ttf"
)

if os.path.exists(FONT_PATH):
    LabelBase.register(
        name="MarathiFont",
        fn_regular=FONT_PATH
    )
    FONT = "MarathiFont"
else:
    FONT = "Roboto"


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Assistant"
        Window.clearcolor = (0.08, 0.10, 0.15, 1)

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(12),
            size_hint_y=None
        )
        root.bind(minimum_height=root.setter("height"))

        title = Label(
            text="[b]🛡️ सुरक्षा सहाय्यक[/b]",
            markup=True,
            font_name=FONT,
            font_size="26sp",
            size_hint_y=None,
            height=dp(65)
        )
        root.add_widget(title)

        subtitle = Label(
            text="नमस्कार! मी तुमचा Security Assistant आहे.",
            font_name=FONT,
            font_size="17sp",
            size_hint_y=None,
            height=dp(60)
        )
        root.add_widget(subtitle)

        self.output = TextInput(
            text="येथे उत्तर दिसेल.",
            font_name=FONT,
            readonly=True,
            multiline=True,
            font_size="17sp",
            size_hint_y=None,
            height=dp(180),
            background_color=(0.14, 0.17, 0.23, 1),
            foreground_color=(1, 1, 1, 1)
        )
        root.add_widget(self.output)

        self.command = TextInput(
            hint_text="इथे कमांड लिहा...",
            font_name=FONT,
            multiline=False,
            font_size="18sp",
            size_hint_y=None,
            height=dp(55)
        )
        self.command.bind(
            on_text_validate=self.run_command
        )
        root.add_widget(self.command)

        run_button = Button(
            text="कमांड चालवा",
            font_name=FONT,
            font_size="18sp",
            size_hint_y=None,
            height=dp(55)
        )
        run_button.bind(on_press=self.run_command)
        root.add_widget(run_button)

        help_button = Button(
            text="मदत",
            font_name=FONT,
            font_size="18sp",
            size_hint_y=None,
            height=dp(55)
        )
        help_button.bind(on_press=self.show_help)
        root.add_widget(help_button)

        footer = Label(
            text="सुरक्षित रहा • विचारपूर्वक इंटरनेट वापरा",
            font_name=FONT,
            font_size="13sp",
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(footer)

        scroll.add_widget(root)
        return scroll

    def run_command(self, instance):
        command = self.command.text.strip().lower()

        if command in ("hello", "hi", "namaskar", "नमस्कार"):
            self.output.text = (
                "नमस्कार! मी तुमचा Security Assistant आहे."
            )

        elif command in ("status", "स्थिती"):
            self.output.text = "ॲप व्यवस्थित सुरू आहे."

        elif command in ("security", "सुरक्षा"):
            self.output.text = (
                "सुरक्षा सूचना:\n"
                "1. मजबूत पासवर्ड वापरा.\n"
                "2. OTP कोणालाही सांगू नका.\n"
                "3. अनोळखी लिंक उघडू नका.\n"
                "4. ॲप्स विश्वसनीय ठिकाणाहूनच इन्स्टॉल करा."
            )

        elif command in ("help", "मदत"):
            self.show_help(instance)
            self.command.text = ""
            return

        elif command == "":
            self.output.text = "कृपया आधी कमांड लिहा."

        else:
            self.output.text = (
                "ही कमांड समजली नाही.\n"
                "मदत बटण दाबा किंवा help लिहा."
            )

        self.command.text = ""

    def show_help(self, instance):
        self.output.text = (
            "उपलब्ध कमांड:\n\n"
            "hello - नमस्कार\n"
            "status - ॲपची स्थिती\n"
            "security - सुरक्षा सूचना\n"
            "help - मदत\n\n"
            "कमांड बॉक्समध्ये कमांड लिहा "
            "आणि 'कमांड चालवा' दाबा."
        )


if __name__ == "__main__":
    SecurityAssistantApp().run()
