
from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget

Window.clearcolor = (0.035, 0.055, 0.09, 1)

LabelBase.register(
    name="MarathiFont",
    fn_regular="NotoSansDevanagari.ttf"
)

GREEN = (0.0, 0.85, 0.57, 1)
WHITE = (0.94, 0.97, 1, 1)
MUTED = (0.65, 0.72, 0.81, 1)
CARD = (0.075, 0.105, 0.16, 1)


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Assistant"

        root = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12)
        )

        scroll = ScrollView(
            do_scroll_x=False
        )

        page = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            size_hint_y=None,
            padding=[0, dp(8), 0, dp(16)]
        )
        page.bind(minimum_height=page.setter("height"))

        page.add_widget(Label(
            text="MOBILE PROTECTION",
            font_name="MarathiFont",
            font_size=dp(24),
            bold=True,
            color=WHITE,
            size_hint_y=None,
            height=dp(45)
        ))

        page.add_widget(Label(
            text="तुमच्या मोबाइलची सुरक्षा",
            font_name="MarathiFont",
            font_size=dp(16),
            color=MUTED,
            size_hint_y=None,
            height=dp(32)
        ))

        page.add_widget(Widget(size_hint_y=None, height=dp(8)))

        page.add_widget(Label(
            text="[  ✓  ]",
            font_size=dp(58),
            bold=True,
            color=GREEN,
            size_hint_y=None,
            height=dp(100)
        ))

        page.add_widget(Label(
            text="SECURITY ASSISTANT",
            font_size=dp(18),
            bold=True,
            color=GREEN,
            size_hint_y=None,
            height=dp(36)
        ))

        self.status = Label(
            text="सुरक्षा तपासणी सुरू करण्यासाठी पर्याय निवडा.",
            font_name="MarathiFont",
            font_size=dp(14),
            color=WHITE,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(58)
        )
        self.status.bind(
            size=lambda obj, size:
            setattr(obj, "text_size", size)
        )
        page.add_widget(self.status)

        self.add_card(
            page,
            "APP SECURITY",
            "ॲप सुरक्षिततेबद्दल माहिती",
            "ॲप सुरक्षा",
            "Android Settings मधील App permissions तपासा."
        )

        self.add_card(
            page,
            "WI-FI SECURITY",
            "Wi-Fi नेटवर्क सुरक्षित ठेवा",
            "Wi-Fi सुरक्षा",
            "अनोळखी Wi-Fi नेटवर्क वापरताना काळजी घ्या."
        )

        self.add_card(
            page,
            "WEB PROTECTION",
            "इंटरनेट वापरताना सावध राहा",
            "वेब सुरक्षा",
            "संशयास्पद लिंक आणि बनावट वेबसाइट टाळा."
        )

        self.add_card(
            page,
            "DEVICE SECURITY",
            "मोबाइल संरक्षणाच्या सूचना",
            "डिव्हाइस सुरक्षा",
            "Screen lock, Android updates आणि Play Protect तपासा."
        )

        page.add_widget(Widget(size_hint_y=None, height=dp(5)))

        help_button = Button(
            text="मदत",
            font_name="MarathiFont",
            font_size=dp(17),
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=(0.10, 0.24, 0.30, 1),
            color=WHITE
        )
        help_button.bind(
            on_release=lambda *_: self.show_message(
                "ही स्क्रीन सुरक्षा सूचना देते. "
                "प्रत्यक्ष स्कॅनिंग अद्याप जोडलेले नाही."
            )
        )
        page.add_widget(help_button)

        page.add_widget(Label(
            text="सुरक्षित रहा • विचारपूर्वक इंटरनेट वापरा",
            font_name="MarathiFont",
            font_size=dp(12),
            color=MUTED,
            size_hint_y=None,
            height=dp(36)
        ))

        scroll.add_widget(page)
        root.add_widget(scroll)
        return root

    def add_card(self, page, heading, subtitle, button_text, message):
        card = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(142)
        )

        card.add_widget(Label(
            text=heading,
            font_size=dp(17),
            bold=True,
            color=GREEN,
            size_hint_y=None,
            height=dp(30)
        ))

        card.add_widget(Label(
            text=subtitle,
            font_name="MarathiFont",
            font_size=dp(13),
            color=WHITE,
            size_hint_y=None,
            height=dp(28)
        ))

        btn = Button(
            text=button_text,
            font_name="MarathiFont",
            font_size=dp(15),
            size_hint_y=None,
            height=dp(44),
            background_normal="",
            background_color=CARD,
            color=WHITE
        )
        btn.bind(
            on_release=lambda *_: self.show_message(message)
        )
        card.add_widget(btn)
        page.add_widget(card)

    def show_message(self, message):
        self.status.text = message


if __name__ == "__main__":
    SecurityAssistantApp().run()
