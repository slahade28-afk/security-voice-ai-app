from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window


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

        run_button = Button(
            text="Run Command",
            size_hint_y=None,
            height=55
        )
        run_button.bind(on_press=self.run_command)
        layout.add_widget(run_button)

        help_button = Button(
            text="Help",
            size_hint_y=None,
            height=50
        )
        help_button.bind(on_press=self.show_help)
        layout.add_widget(help_button)

        return layout

    def run_command(self, instance):
        command = self.command_input.text.strip().lower()

        if command in ("hello", "hi", "namaskar"):
            response = "Namaskar! Mi tumchi madat karayla tayar aahe."
        elif command in ("help", "madat"):
            response = "Commands: hello, status, security, help"
        elif command in ("status", "stithi"):
            response = "Security Assistant chalu aahe."
        elif command in ("security", "suraksha"):
            response = "Anolakhi links ughadu naka. OTP ani password konalahi sangu naka."
        else:
            response = "Command samajla nahi. Help button daba."

        self.output.text = response
        self.command_input.text = ""

    def show_help(self, instance):
        self.output.text = "Try kara: hello, status, security, help"


if __name__ == "__main__":
    SecurityAssistantApp().run()
