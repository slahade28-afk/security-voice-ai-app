

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Voice Command AI"
        Window.clearcolor = (0.04, 0.07, 0.12, 1)

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        root = BoxLayout(
            orientation="vertical",
            padding=16,
            spacing=12,
            size_hint_y=None
        )
        root.bind(minimum_height=root.setter("height"))

        title = Label(
            text="[b]SECURITY AI ASSISTANT[/b]",
            markup=True,
            font_size="22sp",
            size_hint_y=None,
            height=65
        )
        root.add_widget(title)

        subtitle = Label(
            text="Your Personal Security Helper",
            font_size="14sp",
            size_hint_y=None,
            height=35
        )
        root.add_widget(subtitle)

        self.output = Label(
            text="Namaskar! Mi tumcha Security Assistant aahe.",
            font_size="17sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=120
        )
        self.output.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )
        root.add_widget(self.output)

        self.command = TextInput(
            hint_text="Command liha...",
            multiline=False,
            size_hint_y=None,
            height=52
        )
        self.command.bind(on_text_validate=self.run_command)
        root.add_widget(self.command)

        run_button = Button(
            text="RUN COMMAND",
            size_hint_y=None,
            height=55
        )
        run_button.bind(on_press=self.run_command)
        root.add_widget(run_button)

        help_button = Button(
            text="HELP",
            size_hint_y=None,
            height=48
        )
        help_button.bind(on_press=self.show_help)
        root.add_widget(help_button)

        footer = Label(
            text="Stay Safe - Protect Your Privacy",
            font_size="12sp",
            size_hint_y=None,
            height=35
        )
        root.add_widget(footer)

        scroll.add_widget(root)
        return scroll

    def run_command(self, instance):
        command = self.command.text.lower().strip()

        if command in ("hello", "hi", "namaskar"):
            self.output.text = (
                "Namaskar! Mi tumchi madat karayla tayar aahe."
            )
        elif command == "status":
            self.output.text = "Security Assistant chalu aahe."
        elif command == "security":
            self.output.text = (
                "Security Tip: OTP ani password konalahi sangu naka."
            )
        elif command == "help":
            self.show_help(instance)
        else:
            self.output.text = (
                "Command samajla nahi. HELP button daba."
            )

    def show_help(self, instance):
    self.output.text = (
        "उपलब्ध आदेश:\n"
        "hello - नमस्कार\n"
        "status - ॲपची स्थिती\n"
        "security - सुरक्षा सूचना\n"
        "help - मदत"
    
        )


if __name__ == "__main__":
    SecurityAssistantApp().run()

