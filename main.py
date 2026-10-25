from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class SecurityAssistant(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        layout.add_widget(Label(
            text="Security Voice Command AI",
            font_size=24
        ))

        self.command = TextInput(
            hint_text="Command liha...",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.command)

        self.result = Label(text="Namaskar! Mi tuza Security Assistant aahe.")
        layout.add_widget(self.result)

        button = Button(
            text="Run Command",
            size_hint_y=None,
            height=55
        )
        button.bind(on_press=self.run_command)
        layout.add_widget(button)

        return layout

    def run_command(self, instance):
        command = self.command.text.lower().strip()

        if command in ("hello", "namaskar"):
            self.result.text = "Namaskar! Mi tuzi madat karen."
        elif command == "help":
            self.result.text = "Available command: hello, namaskar, help"
        else:
            self.result.text = "Command olakhata aali nahi."

SecurityAssistant().run()
