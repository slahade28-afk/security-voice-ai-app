
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
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "NotoSansDevanagari.ttf")

FONT = "Roboto"

if os.path.exists(FONT_PATH):
    LabelBase.register(
        name="MarathiFont",
        fn_regular=FONT_PATH
    )
    FONT = "MarathiFont"

Window.clearcolor = (0.055, 0.075, 0.12, 1)


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Assistant"

        root = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12)
        )

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        page = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=(0, dp(8), 0, dp(12))
        )
        page.bind(minimum_height=page.setter("height"))

        title = Label(
            text="सुरक्षा सहाय्यक",
            font_name=FONT,
            font_size=dp(25),
            bold=True,
            color=(0.35, 0.85, 1, 1),
            size_hint_y=None,
            height=dp(52),
            halign="center",
            valign="middle"
        )
        title.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )
        page.add_widget(title)

        subtitle = Label(
            text="तुमचा Smart Security Dashboard",
            font_name=FONT,
            font_size=dp(15),
            color=(0.85, 0.9, 1, 1),
            size_hint_y=None,
            height=dp(35),
            halign="center",
            valign="middle"
        )
        subtitle.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )
        page.add_widget(subtitle)

        self.output = Label(
            text=(
                "नमस्कार!\n\n"
                "मी तुमचा Security Assistant आहे.\n"
                "खालील बटणे वापरून सुरुवात करा."
            ),
            font_name=FONT,
            font_size=dp(16),
            color=(1, 1, 1, 1),
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(180),
            padding=(dp(14), dp(14))
        )
        self.output.bind(
            width=lambda obj, val:
            setattr(
                obj,
                "text_size",
                (max(0, val - dp(28)), None)
            )
        )
        page.add_widget(self.output)

        self.command = TextInput(
            hint_text="कमांड येथे लिहा...",
            font_name=FONT,
            font_size=dp(16),
            multiline=False,
            size_hint_y=None,
            height=dp(52),
            padding=(dp(12), dp(12)),
            background_color=(0.93, 0.95, 0.98, 1),
            foreground_color=(0.08, 0.1, 0.15, 1),
            cursor_color=(0.1, 0.35, 0.8, 1)
        )
        self.command.bind(
            on_text_validate=self.run_command
        )
        page.add_widget(self.command)

        run_button = self.make_button(
            "कमांड चालवा",
            (0.05, 0.48, 0.78, 1),
            self.run_command
        )
        page.add_widget(run_button)

        grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(104)
        )

        grid.add_widget(
            self.make_button(
                "🛡️ सुरक्षा",
                (0.08, 0.52, 0.36, 1),
                self.show_security
            )
        )

        grid.add_widget(
            self.make_button(
                "📊 स्थिती",
                (0.12, 0.38, 0.56, 1),
                self.show_status
            )
        )

        grid.add_widget(
            self.make_button(
                "📘 मदत",
                (0.34, 0.32, 0.55, 1),
                self.show_help
            )
        )

        grid.add_widget(
            self.make_button(
                "🎙️ Voice",
                (0.40, 0.30, 0.65, 1),
                self.show_voice_info
            )
        )

        page.add_widget(grid)

        footer = Label(
            text="सुरक्षित रहा • विचारपूर्वक इंटरनेट वापरा",
            font_name=FONT,
            font_size=dp(11),
            color=(0.65, 0.75, 0.85, 1),
            size_hint_y=None,
            height=dp(32),
            halign="center",
            valign="middle"
        )
        footer.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )
        page.add_widget(footer)

        scroll.add_widget(page)
        root.add_widget(scroll)

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

        if command in (
            "hello", "hi", "namaskar", "नमस्कार"
        ):
            message = (
                "नमस्कार!\n\n"
                "मी तुमचा Security Assistant आहे."
            )

        elif command in ("status", "स्थिती"):
            self.show_status(instance)
            self.command.text = ""
            return

        elif command in (
            "security", "सुरक्षा"
        ):
            self.show_security(instance)
            self.command.text = ""
            return

        elif command in ("help", "मदत"):
            self.show_help(instance)
            self.command.text = ""
            return

        elif command == "":
            message = "कृपया आधी कमांड लिहा."

        else:
            message = (
                "ही कमांड समजली नाही.\n\n"
                "उपलब्ध कमांड:\n"
                "hello, status, security, help"
            )

        self.output.text = message
        self.command.text = ""

    def show_status(self, instance):
        self.output.text = (
            "📊 ॲपची स्थिती\n\n"
            "ॲप सुरू आहे.\n"
            "कमांड सुविधा उपलब्ध आहे.\n"
            "सुरक्षा सूचना उपलब्ध आहेत.\n\n"
            "टीप: ही सामान्य ॲप स्थिती आहे; "
            "फोनचे संपूर्ण सुरक्षा स्कॅन नाही."
        )

    def show_security(self, instance):
        self.output.text = (
            "🛡️ सुरक्षा सूचना\n\n"
            "१. OTP आणि PIN गुप्त ठेवा.\n"
            "२. मजबूत पासवर्ड वापरा.\n"
            "३. अनोळखी लिंक उघडू नका.\n"
            "४. फोन आणि ॲप्स अपडेट ठेवा.\n"
            "५. दोन-स्तरीय सुरक्षा सुरू करा.\n"
            "६. संशयास्पद ॲप्स टाळा."
        )

    def show_help(self, instance):
        self.output.text = (
            "📘 उपलब्ध कमांड\n\n"
            "hello - नमस्कार\n"
            "status - ॲपची स्थिती\n"
            "security - सुरक्षा सूचना\n"
            "help - मदत\n\n"
            "कमांड बॉक्समध्ये कमांड लिहा "
            "आणि कमांड चालवा हे बटण दाबा."
        )

    def show_voice_info(self, instance):
        self.output.text = (
            "🎙️ Voice Command\n\n"
            "आवाजाद्वारे कमांड देण्याची "
            "सुविधा पुढे जोडता येईल.\n\n"
            "सध्या कमांड बॉक्स वापरा."
        )


if __name__ == "__main__":
    SecurityAssistantApp().run()
