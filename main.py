import time
import os
import re
import json
import hashlib
import secrets
import struct
import shutil
import tempfile
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


Window.clearcolor = (0.035, 0.055, 0.09, 1)

FONT = "Roboto"

if os.path.exists("NotoSansDevanagari.ttf"):
    LabelBase.register(
        name="MarathiFont",
        fn_regular="NotoSansDevanagari.ttf"
    )
    FONT = "MarathiFont"

BG = (0.035, 0.055, 0.09, 1)
CARD = (0.075, 0.105, 0.16, 1)
GREEN = (0.0, 0.85, 0.57, 1)
WHITE = (0.94, 0.97, 1, 1)
MUTED = (0.65, 0.72, 0.81, 1)


class SecurityAssistantApp(App):

    def build(self):
        self.title = "Security Assistant"
        self.base = self.user_data_dir
        os.makedirs(self.base, exist_ok=True)

        self.vault_dir = os.path.join(self.base, "vault")
        os.makedirs(self.vault_dir, exist_ok=True)

        self.pin_file = os.path.join(self.base, "vault_pin.json")
        self.log_file = os.path.join(self.base, "activity.json")

        self.vault_pin = None
        self.pin_failed_attempts = 0
        self.pin_lockout_until = 0

        root = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10)
        )

        scroll = ScrollView(do_scroll_x=False)

        self.page = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[0, dp(8), 0, dp(20)]
        )

        self.page.bind(minimum_height=self.page.setter("height"))
        scroll.add_widget(self.page)
        root.add_widget(scroll)

        self.show_dashboard()

        try:
            from android import activity
            activity.bind(on_activity_result=self.on_activity_result)
        except Exception:
            pass

        return root

    def label(self, text, size=15, color=WHITE, height=45):
        return Label(
            text=text,
            font_name=FONT,
            font_size=dp(size),
            color=color,
            size_hint_y=None,
            height=dp(height),
            halign="center",
            valign="middle"
        )

    def button(self, text, callback, height=56):
        btn = Button(
            text=text,
            font_name=FONT,
            font_size=dp(15),
            size_hint=(1, None),
            height=dp(height),
            background_normal="",
            background_down="",
            background_color=CARD,
            color=WHITE,
            halign="center",
            valign="middle"
        )
        btn.bind(size=lambda instance, value: setattr(
            instance, "text_size", (value[0] - dp(20), None)
        ))
        btn.bind(on_release=lambda *_: callback())
        return btn

    def reset_page(self, title, subtitle=""):
        self.page.clear_widgets()
        self.page.add_widget(self.label(title, 23, GREEN, 55))

        if subtitle:
            self.page.add_widget(self.label(subtitle, 14, MUTED, 55))

        self.page.add_widget(
            self.button("⌂ मुख्यपृष्ठ", self.show_dashboard, 50)
        )
        if title != "☰ मुख्य मेनू":
            self.page.add_widget(
                self.button("☰ मुख्य मेनू", self.menu_page, 50)
            )

    def message(self, title, message):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        content.add_widget(
            self.label(message, 14, WHITE, 130)
        )

        close = Button(
            text="OK",
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(close)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, None),
            height=dp(250)
        )

        close.bind(on_release=popup.dismiss)
        popup.open()

    def log(self, action, result):
        try:
            entries = []

            if os.path.exists(self.log_file):
                with open(self.log_file, encoding="utf-8") as f:
                    entries = json.load(f)

            entries.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "action": action,
                "result": result
            })

            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(
                    entries[-200:],
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        except Exception:
            pass

    # MAIN DASHBOARD AND NAVIGATION

    def show_dashboard(self):
        self.page.clear_widgets()

        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "images", "cyber_lock.png"
        )

        if os.path.exists(logo_path):
            self.page.add_widget(Image(
                source=logo_path,
                size_hint=(1, None),
                height=dp(125),
                allow_stretch=True,
                keep_ratio=True
            ))
        else:
            self.page.add_widget(self.label("🔐", 48, GREEN, 85))

        self.page.add_widget(self.label("सुरक्षा सहाय्यक", 27, GREEN, 52))
        self.page.add_widget(
            self.label("तुमच्या मोबाइल सुरक्षेसाठी एकाच ठिकाणी साधने",
                       14, MUTED, 55)
        )
        self.page.add_widget(self.label("● सुरक्षा केंद्र", 18, GREEN, 40))

        options = [
            ("🔐  सुरक्षित फाइल व्हॉल्ट", self.vault),
            ("🧰  सर्व सुरक्षा साधने", self.tools_page),
            ("📱  ॲप परवानगी तपासणी", self.permissions),
            ("📶  Wi-Fi सुरक्षा", self.wifi_security),
            ("🛡️  Firewall माहिती", self.firewall_security),
            ("🔗  संशयास्पद लिंक तपासा", self.link_checker),
            ("📋  सुरक्षा इतिहास", self.activity_log),
            ("⚙️  सेटिंग्ज", self.settings_page),
            ("❔  मदत", self.help_page),
            ("ℹ️  ॲपविषयी", self.about_page),
        ]

        for title, callback in options:
            self.page.add_widget(self.button(title, callback, 58))

        self.page.add_widget(self.label(
            "सूचना: Firewall प्रत्यक्ष नेटवर्क ट्रॅफिक ब्लॉक करत नाही.",
            13, MUTED, 55
        ))
        self.page.add_widget(self.label(
            "सुरक्षित रहा • अनोळखी लिंक आणि APK टाळा",
            13, MUTED, 45
        ))

    def menu_page(self):
        self.reset_page("☰ मुख्य मेनू", "आवश्यक विभाग निवडा")

        options = [
            ("🏠  मुख्यपृष्ठ", self.show_dashboard),
            ("🧰  सुरक्षा साधने", self.tools_page),
            ("🔐  सुरक्षित फाइल व्हॉल्ट", self.vault),
            ("📱  ॲप परवानग्या", self.permissions),
            ("📶  Wi-Fi सुरक्षा", self.wifi_security),
            ("🛡️  Firewall माहिती", self.firewall_security),
            ("🔗  लिंक तपासणी", self.link_checker),
            ("📋  इतिहास", self.activity_log),
            ("⚙️  सेटिंग्ज", self.settings_page),
            ("❔  मदत", self.help_page),
            ("ℹ️  ॲपविषयी", self.about_page),
        ]

        for title, callback in options:
            self.page.add_widget(self.button(title, callback, 54))

    def tools_page(self):
        self.reset_page("🧰 सुरक्षा साधने", "तुम्हाला आवश्यक साधन निवडा")

        options = [
            ("🔐 सुरक्षित फाइल व्हॉल्ट", self.vault),
            ("📱 ॲप परवानगी तपासणी", self.permissions),
            ("📶 Wi-Fi सुरक्षा मार्गदर्शन", self.wifi_security),
            ("🛡️ Firewall स्थिती", self.firewall_security),
            ("🔗 संशयास्पद लिंक तपासणी", self.link_checker),
            ("📋 सुरक्षा इतिहास", self.activity_log),
            ("🛡️ मोबाइल संरक्षण", self.mobile_protection),
        ]

        for title, callback in options:
            self.page.add_widget(self.button(title, callback, 58))

    def settings_page(self):
        self.reset_page("⚙️ सेटिंग्ज", "ॲप आणि मोबाइलच्या सुरक्षा सेटिंग्ज")

        self.page.add_widget(self.label(
            "या आवृत्तीत स्वतंत्र थीम किंवा भाषा बदलण्याची सुविधा नाही.",
            14, MUTED, 65
        ))
        self.page.add_widget(self.button(
            "📱 या ॲपच्या Android सेटिंग्ज उघडा",
            self.open_app_settings, 58
        ))
        self.page.add_widget(self.button(
            "🔐 सुरक्षित फाइल व्हॉल्ट",
            self.vault, 58
        ))
        self.page.add_widget(self.button(
            "📋 सुरक्षा इतिहास पाहा",
            self.activity_log, 58
        ))

    def help_page(self):
        self.reset_page("❔ मदत", "सुरक्षा सहाय्यक कसा वापरावा")

        help_text = (
            "• सुरक्षित फाइल व्हॉल्ट: PIN वापरून फाइल एन्क्रिप्ट किंवा Restore करा.\n\n"
            "• लिंक तपासणी: संशयास्पद लिंकची प्राथमिक तपासणी करा.\n\n"
            "• Wi-Fi सुरक्षा: सुरक्षित नेटवर्क वापरण्याच्या सूचना वाचा.\n\n"
            "• ॲप परवानग्या: Android सेटिंग्जमध्ये परवानग्या तपासा.\n\n"
            "• इतिहास: ॲपमध्ये नोंदवलेल्या काही क्रिया पाहा.\n\n"
            "ही साधने संपूर्ण मोबाइल स्कॅन करत नाहीत. "
            "लिंक तपासणी सुरक्षिततेची हमी देत नाही."
        )
        self.page.add_widget(self.label(help_text, 14, WHITE, 300))

    def about_page(self):
        self.reset_page("ℹ️ ॲपविषयी", "Security Assistant")

        self.page.add_widget(self.label(
            "तुमच्या मोबाइल सुरक्षेसाठी तयार केलेले सहाय्यक ॲप.",
            16, WHITE, 70
        ))
        self.page.add_widget(self.label(
            "उपलब्ध सुविधा: सुरक्षित फाइल व्हॉल्ट, प्राथमिक लिंक तपासणी, "
            "Wi-Fi मार्गदर्शन, परवानगी तपासणी आणि सुरक्षा इतिहास.",
            14, MUTED, 110
        ))
        self.page.add_widget(self.label(
            "महत्त्वाचे: Firewall ट्रॅफिक फिल्टरिंग सक्रिय नाही. "
            "हे ॲप पूर्ण अँटीव्हायरस किंवा संपूर्ण डिव्हाइस स्कॅनर नाही.",
            14, GREEN, 100
        ))

    # SECURE VAULT

    def derive_key(self, pin, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=300000
        )
        return kdf.derive(pin.encode("utf-8"))

    def vault(self):
        self.reset_page(
            "🔐 SECURE VAULT",
            "Unlock the Vault with your PIN"
        )

        if not os.path.exists(self.pin_file):
            self.page.add_widget(
                self.label(
                    "Create a new PIN with at least 6 digits.",
                    14,
                    WHITE,
                    55
                )
            )

            pin = TextInput(
                hint_text="New PIN",
                password=True,
                multiline=False,
                size_hint_y=None,
                height=dp(48)
            )

            confirm = TextInput(
                hint_text="Confirm PIN",
                password=True,
                multiline=False,
                size_hint_y=None,
                height=dp(48)
            )

            self.page.add_widget(pin)
            self.page.add_widget(confirm)

            def create_pin():
                if not pin.text.isdigit() or len(pin.text) < 6:
                    self.message(
                        "PIN",
                        "Use a PIN with at least 6 digits."
                    )
                    return

                if pin.text != confirm.text:
                    self.message(
                        "PIN",
                        "The PINs do not match."
                    )
                    return

                salt = secrets.token_bytes(16)

                digest = hashlib.pbkdf2_hmac(
                    "sha256",
                    pin.text.encode(),
                    salt,
                    300000
                ).hex()

                with open(self.pin_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "salt": salt.hex(),
                        "hash": digest
                    }, f)

                self.vault_pin = pin.text
                self.log("Vault PIN", "PIN created")
                self.vault_files()

            self.page.add_widget(
                self.button("Create PIN", create_pin)
            )
            return

        pin = TextInput(
            hint_text="Vault PIN",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )

        self.page.add_widget(pin)

        def unlock():
            now = time.monotonic()

            if now < self.pin_lockout_until:
                remaining = int(self.pin_lockout_until - now) + 1
                self.message(
                    "Vault",
                    f"Too many failed attempts. Wait {remaining} seconds."
                )
                return

            try:
                with open(self.pin_file, encoding="utf-8") as f:
                    saved = json.load(f)

                digest = hashlib.pbkdf2_hmac(
                    "sha256",
                    pin.text.encode(),
                    bytes.fromhex(saved["salt"]),
                    300000
                ).hex()

                if secrets.compare_digest(digest, saved["hash"]):
                    self.pin_failed_attempts = 0
                    self.pin_lockout_until = 0
                    self.vault_pin = pin.text
                    self.vault_files()

                else:
                    self.pin_failed_attempts += 1
                    remaining = 3 - self.pin_failed_attempts

                    if self.pin_failed_attempts >= 3:
                        self.pin_failed_attempts = 0
                        self.pin_lockout_until = time.monotonic() + 30

                        self.message(
                            "Vault",
                            "3 incorrect PIN attempts. Vault locked for 30 seconds."
                        )
                    else:
                        self.message(
                            "Vault",
                            f"Incorrect PIN. Attempts remaining: {remaining}"
                        )

            except Exception:
                self.message(
                    "Vault",
                    "Could not read PIN data."
                )

        self.page.add_widget(
            self.button("Unlock Vault", unlock)
        )

    def encrypt_file(self, source, destination, pin):
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        key = self.derive_key(pin, salt)

        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce)
        ).encryptor()

        temp = destination + ".tmp"

        try:
            with open(source, "rb") as src, open(temp, "wb") as dst:
                dst.write(b"SAV1" + salt + nonce)

                filename = os.path.basename(source).encode("utf-8")
                metadata = struct.pack(">I", len(filename)) + filename

                dst.write(encryptor.update(metadata))

                while True:
                    chunk = src.read(1024 * 1024)

                    if not chunk:
                        break

                    dst.write(encryptor.update(chunk))

                dst.write(encryptor.finalize())
                dst.write(encryptor.tag)

            os.replace(temp, destination)

        except Exception:
            if os.path.exists(temp):
                os.remove(temp)
            raise

    def decrypt_file(self, encrypted_path, output_dir, pin):
        temp_path = None

        try:
            size = os.path.getsize(encrypted_path)

            if size < 48:
                raise ValueError("Vault file is incomplete.")

            with open(encrypted_path, "rb") as src:
                header = src.read(32)

                if len(header) != 32 or header[:4] != b"SAV1":
                    raise ValueError("Invalid file format.")

                salt = header[4:20]
                nonce = header[20:32]
                key = self.derive_key(pin, salt)

                src.seek(size - 16)
                tag = src.read(16)
                src.seek(32)

                decryptor = Cipher(
                    algorithms.AES(key),
                    modes.GCM(nonce, tag)
                ).decryptor()

                fd, temp_path = tempfile.mkstemp(
                    dir=self.vault_dir
                )

                remaining = size - 48

                with os.fdopen(fd, "wb") as tmp:
                    while remaining:
                        chunk = src.read(
                            min(1024 * 1024, remaining)
                        )

                        if not chunk:
                            raise ValueError("File is incomplete.")

                        tmp.write(decryptor.update(chunk))
                        remaining -= len(chunk)

                    tmp.write(decryptor.finalize())

            with open(temp_path, "rb") as tmp:
                raw = tmp.read(4)

                if len(raw) != 4:
                    raise ValueError("Invalid file information.")

                n = struct.unpack(">I", raw)[0]

                if n < 1 or n > 4096:
                    raise ValueError("Invalid file name.")

                name = tmp.read(n).decode("utf-8")
                name = os.path.basename(name.replace("\\", "/"))

                if not name:
                    raise ValueError("File name is empty.")

                out = os.path.join(output_dir, name)

                if os.path.exists(out):
                    stem, ext = os.path.splitext(name)
                    out = os.path.join(
                        output_dir,
                        stem + "_" + secrets.token_hex(4) + ext
                    )

                fd, safe_out = tempfile.mkstemp(dir=output_dir)

                try:
                    with os.fdopen(fd, "wb") as dst, open(
                        temp_path, "rb"
                    ) as tmp:
                        tmp.seek(4 + n)
                        shutil.copyfileobj(tmp, dst)

                    os.replace(safe_out, out)

                except Exception:
                    if os.path.exists(safe_out):
                        os.remove(safe_out)
                    raise

            return out

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def vault_files(self):
        self.reset_page(
            "🔐 ENCRYPTED VAULT",
            "AES-256-GCM encryption"
        )

        self.page.add_widget(
            self.label(
                "The original file is not deleted automatically. Verify the restored file.",
                13,
                MUTED,
                75
            )
        )

        try:
            from plyer import filechooser

            self.page.add_widget(
                self.button(
                    "＋ Select a File and Encrypt",
                    lambda: filechooser.open_file(
                        on_selection=self.copy_selected
                    ),
                    54
                )
            )

            files = sorted(
                x for x in os.listdir(self.vault_dir)
                if x.endswith(".sav")
            )

            if not files:
                self.page.add_widget(
                    self.label("No files available yet.", 14)
                )

            for name in files:
                self.page.add_widget(
                    self.label(name, 12, WHITE, 34)
                )

                self.page.add_widget(
                    self.button(
                        "Restore: " + name[:22],
                        lambda name=name: self.restore_file(name),
                        46
                    )
                )

        except Exception as exc:
            self.page.add_widget(
                self.label(
                    "File chooser unavailable: " + str(exc),
                    12,
                    MUTED,
                    70
                )
            )

    def copy_selected(self, selection):
        if not selection:
            return

        try:
            source = selection[0]

            if not os.path.isfile(source):
                raise ValueError("File not found.")

            name = secrets.token_hex(16) + ".sav"
            destination = os.path.join(self.vault_dir, name)

            self.encrypt_file(
                source,
                destination,
                self.vault_pin
            )

            self.log("Vault Encrypt", os.path.basename(source))

            self.message(
                "Encryption Successful",
                "File encrypted. The original file has not been deleted."
            )

            self.vault_files()

        except Exception as exc:
            self.message("Encryption Error", str(exc))

    def restore_file(self, name):
        try:
            from jnius import autoclass

            encrypted_path = os.path.join(self.vault_dir, name)
            temp_dir = tempfile.mkdtemp(dir=self.base)

            try:
                restored_path = self.decrypt_file(
                    encrypted_path,
                    temp_dir,
                    self.vault_pin
                )

                self._restore_temp_path = restored_path
                self._restore_temp_dir = temp_dir

                Intent = autoclass("android.content.Intent")

                PythonActivity = autoclass(
                    "org.kivy.android.PythonActivity"
                )

                activity = PythonActivity.mActivity

                intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
                intent.addCategory(Intent.CATEGORY_OPENABLE)
                intent.setType("*/*")

                intent.putExtra(
                    Intent.EXTRA_TITLE,
                    os.path.basename(restored_path)
                )

                self._restore_activity = activity
                self._restore_request_code = 7412

                activity.startActivityForResult(intent, 7412)

                self.message(
                    "Save Restored File",
                    "In the Android save window, select Downloads or another folder."
                )

            except Exception:
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise

        except Exception as exc:
            self.message("Restore Failed", str(exc))

    def on_activity_result(self, request_code, result_code, intent):
        try:
            if request_code != 7412:
                return

            if not hasattr(self, "_restore_temp_path"):
                return

            if result_code != -1 or intent is None:
                self.message(
                    "Restore Cancelled",
                    "File was not saved."
                )
                return

            uri = intent.getData()

            if uri is None:
                raise ValueError("No save location was selected.")

            resolver = self._restore_activity.getContentResolver()
            stream = resolver.openOutputStream(uri)

            if stream is None:
                raise ValueError("Could not open save location.")

            try:
                with open(self._restore_temp_path, "rb") as src:
                    while True:
                        chunk = src.read(1024 * 1024)

                        if not chunk:
                            break

                        stream.write(bytearray(chunk))

            finally:
                stream.close()

            self.log(
                "Vault Restore",
                os.path.basename(self._restore_temp_path)
            )

            self.message(
                "Restore Successful",
                "File saved successfully."
            )

        except Exception as exc:
            self.message("Restore Failed", str(exc))

        finally:
            temp_dir = getattr(self, "_restore_temp_dir", None)

            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)

            for attr in (
                "_restore_temp_path",
                "_restore_temp_dir",
                "_restore_activity",
                "_restore_request_code"
            ):
                if hasattr(self, attr):
                    delattr(self, attr)

    # APP PERMISSIONS

    def permissions(self):
        self.reset_page(
            "📱 APP PERMISSIONS",
            "APP PERMISSIONS"
        )

        self.page.add_widget(
            self.label(
                "Check Camera, Microphone, Location, and Photos permissions in Android Settings.",
                14,
                WHITE,
                100
            )
        )

        self.page.add_widget(
            self.button(
                "Open App Settings",
                self.open_app_settings
            )
        )

        self.page.add_widget(
            self.button(
                "Privacy Dashboard Guide",
                lambda: self.message(
                    "Privacy",
                    "Open Settings → Security & privacy → Privacy dashboard."
                )
            )
        )

        self.log("Permissions", "Viewed tips")

    def open_app_settings(self):
        try:
            from jnius import autoclass

            activity = autoclass(
                "org.kivy.android.PythonActivity"
            ).mActivity

            Settings = autoclass("android.provider.Settings")
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")

            intent = Intent(
                Settings.ACTION_APPLICATION_DETAILS_SETTINGS
            )

            intent.setData(
                Uri.parse("package:" + activity.getPackageName())
            )

            activity.startActivity(intent)

        except Exception:
            self.message(
                "Settings",
                "Open Android Settings → Apps → Security Assistant."
            )

    # WI-FI SECURITY

    def wifi_security(self):
        self.reset_page(
            "📶 WI-FI SECURITY",
            "WI-FI SECURITY TIPS"
        )

        tips = [
            "• Avoid banking on unfamiliar Wi-Fi networks.",
            "• Use a strong password for your router.",
            "• Use WPA2 or WPA3.",
            "• Disable auto-connect to unfamiliar networks.",
            "• Be careful when sending sensitive information over public Wi-Fi."
        ]

        for tip in tips:
            self.page.add_widget(
                self.label(tip, 14, WHITE, 60)
            )

        self.page.add_widget(
            self.button(
                "Log Activity",
                lambda: self.log("Wi-Fi", "Viewed tips")
            )
        )


    # FIREWALL SECURITY

    def firewall_security(self):
        self.reset_page(
            "SMART FIREWALL",
            "NETWORK PROTECTION CENTER"
        )

        self.page.add_widget(
            self.label(
                "FIREWALL ENGINE: NOT ACTIVE",
                18, WHITE, 45
            )
        )

        self.page.add_widget(
            self.label(
                "Network Monitor: Not Active",
                14, WHITE, 35
            )
        )

        self.page.add_widget(
            self.label(
                "App Network Rules: Not Configured",
                14, WHITE, 35
            )
        )

        self.page.add_widget(
            self.label(
                "Firewall Activity and Controls",
                17, GREEN, 45
            )
        )

        def open_vpn_settings():
            try:
                from jnius import autoclass

                Settings = autoclass(
                    "android.provider.Settings"
                )
                Intent = autoclass(
                    "android.content.Intent"
                )
                activity = autoclass(
                    "org.kivy.android.PythonActivity"
                ).mActivity

                intent = Intent(
                    Settings.ACTION_VPN_SETTINGS
                )
                activity.startActivity(intent)
                self.log(
                    "Firewall",
                    "Opened Android VPN settings"
                )

            except Exception:
                self.message(
                    "VPN Settings",
                    "Open VPN from Android Settings."
                )

        def run_readiness_check():
            self.log(
                "Firewall",
                "Readiness check requested; traffic blocking is not implemented"
            )
            self.message(
                "Firewall Readiness",
                "Dashboard is available. Real traffic filtering is not installed yet."
            )

        self.page.add_widget(
            self.button(
                "Open Android VPN Settings",
                open_vpn_settings
            )
        )

        self.page.add_widget(
            self.button(
                "Check Firewall Readiness",
                run_readiness_check
            )
        )

        self.page.add_widget(
            self.button(
                "View Security Activity Log",
                self.activity_log
            )
        )

        self.page.add_widget(
            self.label(
                "Next: Android VPN service and traffic filtering engine.",
                13, WHITE, 55
            )
        )
    # FAKE LINK CHECKER

    def link_checker(self):
        self.reset_page(
            "🔗 FAKE LINK CHECKER",
            "CHECK SUSPICIOUS LINKS"
        )

        self.page.add_widget(
            self.label(
                "Paste a link below to check it.",
                14,
                WHITE,
                45
            )
        )

        entry = TextInput(
            hint_text="https://example.com",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        result = self.label(
            "The scan result will appear here.",
            13,
            WHITE,
            110
        )

        self.page.add_widget(entry)
        self.page.add_widget(result)

        def check():
            url = entry.text.strip()
            issues = []

            if not url:
                result.text = "Please enter a link."
                return

            if not re.match(r"^https?://", url, re.I):
                issues.append("Missing http:// or https://")

            if "@" in url:
                issues.append("The link contains an @ symbol.")

            if re.search(
                r"(login|verify|gift|free-prize|password)",
                url,
                re.I
            ):
                issues.append("Suspicious keywords detected.")

            if re.match(
                r"^https?://\d{1,3}(?:\.\d{1,3}){3}",
                url,
                re.I
            ):
                issues.append("The link uses a direct IP address.")

            if issues:
                result.text = "⚠️ WARNING!\n" + "\n".join(issues)

                self.log(
                    "Link Checker",
                    "Suspicious indicators found"
                )

            else:
                result.text = (
                    "No obvious warning signs were detected. "
                    "However, this does not guarantee that the link is safe."
                )

                self.log(
                    "Link Checker",
                    "Initial check completed"
                )

        self.page.add_widget(
            self.button("Check Link", check)
        )

    # ACTIVITY LOG

    def activity_log(self):
        self.reset_page(
            "📋 ACTIVITY LOG",
            "SECURITY ACTIVITY LOG"
        )

        try:
            with open(self.log_file, encoding="utf-8") as f:
                entries = json.load(f)

        except Exception:
            entries = []

        if not entries:
            self.page.add_widget(
                self.label(
                    "No activity recorded yet.",
                    14,
                    WHITE,
                    45
                )
            )

        for item in reversed(entries[-50:]):
            self.page.add_widget(
                self.label(
                    item.get("time", "") + "\n" +
                    item.get("action", "") + ": " +
                    item.get("result", ""),
                    12,
                    WHITE,
                    65
                )
            )

    # MOBILE PROTECTION

    def mobile_protection(self):
        self.reset_page(
            "🛡️ MOBILE PROTECTION",
            "MOBILE SECURITY TIPS"
        )

        tips = [
            "✓ Keep Android updated.",
            "✓ Keep Google Play Protect enabled.",
            "✓ Use a screen lock and a strong PIN.",
            "✓ Do not install APKs from unknown sources.",
            "✓ Back up important files.",
            "✓ Disable unnecessary app permissions."
        ]

        for tip in tips:
            self.page.add_widget(
                self.label(tip, 14, WHITE, 55)
            )

        self.log(
            "Mobile Protection",
            "Viewed tips"
        )


if __name__ == "__main__":
    SecurityAssistantApp().run()
