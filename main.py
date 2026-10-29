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

    def button(self, text, callback, height=50):
        btn = Button(
            text=text,
            font_name=FONT,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(height),
            background_normal="",
            background_color=CARD,
            color=WHITE
        )
        btn.bind(on_release=lambda *_: callback())
        return btn

    def reset_page(self, title, subtitle=""):
        self.page.clear_widgets()

        self.page.add_widget(
            self.label(title, 23, GREEN, 55)
        )

        if subtitle:
            self.page.add_widget(
                self.label(subtitle, 14, MUTED, 50)
            )

        self.page.add_widget(
            self.button("⌂ Main Dashboard", self.show_dashboard)
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

    # MAIN DASHBOARD

    def show_dashboard(self):
        self.page.clear_widgets()

        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "images",
            "cyber_lock.png"
        )

        if os.path.exists(logo_path):
            logo = Image(
                source=logo_path,
                size_hint=(1, None),
                height=dp(155),
                allow_stretch=True,
                keep_ratio=True
            )
            self.page.add_widget(logo)
        else:
            self.page.add_widget(
                self.label("🔐", 55, GREEN, 100)
            )

        self.page.add_widget(
            self.label("SECURITY ASSISTANT", 23, GREEN, 48)
        )

        self.page.add_widget(
            self.label("SMART MOBILE PROTECTION", 15, WHITE, 38)
        )

        self.page.add_widget(
            self.label(
                "तुमच्या मोबाईलची सुरक्षा, एकाच ठिकाणी",
                16,
                MUTED,
                55
            )
        )

        self.page.add_widget(
            self.label("✓ SECURITY DASHBOARD", 18, GREEN, 45)
        )

        options = [
            ("🔐  Secure Vault", self.vault),
            ("📱  App Permission Checker", self.permissions),
            ("📶  Wi-Fi Security", self.wifi_security),
            ("🛡️  Firewall Security", self.firewall_security),

            ("🔗  Fake Link Checker", self.link_checker),
            ("📋  Security Activity Log", self.activity_log),
            ("🛡️  Mobile Protection", self.mobile_protection)
        ]

        for title, callback in options:
            self.page.add_widget(
                self.button(title, callback, 56)
            )

        self.page.add_widget(
            self.label(
                "सुरक्षित रहा • संशयास्पद लिंक टाळा",
                13,
                MUTED,
                45
            )
        )

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
                    "किमान 6 अंकांचा नवीन PIN तयार करा.",
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
                        "किमान 6 अंकांचा PIN वापरा."
                    )
                    return

                if pin.text != confirm.text:
                    self.message(
                        "PIN",
                        "दोन्ही PIN जुळत नाहीत."
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
                    f"खूप चुकीचे प्रयत्न झाले. {remaining} सेकंद थांबा."
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
                            "3 चुकीचे PIN. Vault 30 सेकंद लॉक."
                        )
                    else:
                        self.message(
                            "Vault",
                            f"चुकीचा PIN. उरलेले प्रयत्न: {remaining}"
                        )

            except Exception:
                self.message(
                    "Vault",
                    "PIN माहिती वाचता आली नाही."
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
                "मूळ फाइल आपोआप हटवली जात नाही. Restore तपासून पाहा.",
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
                    self.label("अजून कोणतीही फाइल नाही.", 14)
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
                    "File chooser उपलब्ध नाही: " + str(exc),
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
                "फाइल एन्क्रिप्ट झाली. मूळ फाइल हटवलेली नाही."
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
                    "Android save window मध्ये Downloads किंवा दुसरे फोल्डर निवडा."
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
                    "फाइल सेव्ह केलेली नाही."
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
                "फाइल यशस्वीपणे सेव्ह झाली."
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
            "मोबाईल ॲप परवानग्या"
        )

        self.page.add_widget(
            self.label(
                "Camera, Microphone, Location आणि Photos परवानग्या Android Settings मध्ये तपासा.",
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
                    "Settings → Security & privacy → Privacy dashboard उघडा."
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
                "Android Settings → Apps → Security Assistant उघडा."
            )

    # WI-FI SECURITY

    def wifi_security(self):
        self.reset_page(
            "📶 WI-FI SECURITY",
            "Wi-Fi सुरक्षित ठेवण्यासाठी सूचना"
        )

        tips = [
            "• अनोळखी Wi-Fi वर बँकिंग टाळा.",
            "• Router साठी मजबूत पासवर्ड ठेवा.",
            "• WPA2 किंवा WPA3 वापरा.",
            "• अनोळखी नेटवर्कचे Auto-connect बंद करा.",
            "• सार्वजनिक Wi-Fi वर संवेदनशील माहिती पाठवताना काळजी घ्या."
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
            "🛡️ FIREWALL SECURITY",
            "नेटवर्क सुरक्षिततेसाठी मार्गदर्शन"
        )

        tips = [
            "✓ अनोळखी Wi-Fi नेटवर्क टाळा.",
            "✓ Android मधील VPN सेटिंग तपासा.",
            "✓ विश्वासार्ह VPN सेवा वापरताना तिची गोपनीयता नीती वाचा.",
            "✓ अनावश्यक VPN प्रोफाइल वापरू नका.",
            "✓ संशयास्पद ॲप्स आणि त्यांच्या परवानग्या तपासा.",
            "⚠️ ही स्क्रीन स्वतः नेटवर्क ट्रॅफिक ब्लॉक करत नाही."
        ]

        for tip in tips:
            self.page.add_widget(
                self.label(tip, 14, WHITE, 58)
            )

        def open_vpn_settings():
            try:
                from jnius import autoclass

                Settings = autoclass("android.provider.Settings")
                Intent = autoclass("android.content.Intent")
                activity = autoclass(
                    "org.kivy.android.PythonActivity"
                ).mActivity

                intent = Intent(Settings.ACTION_VPN_SETTINGS)
                activity.startActivity(intent)

                self.log("Firewall", "Opened Android VPN settings")

            except Exception:
                self.message(
                    "VPN Settings",
                    "Android Settings मध्ये VPN शोधून उघडा."
                )

        self.page.add_widget(
            self.button(
                "Open Android VPN Settings",
                open_vpn_settings
            )
        )

        self.page.add_widget(
            self.button(
                "Log Security Check",
                lambda: (
                    self.log("Firewall", "Security guidance viewed"),
                    self.message(
                        "Firewall",
                        "नोंद केली. फोनवर प्रत्यक्ष Firewall सक्रिय झालेला नाही."
                    )
                )
            )
        )

    # FAKE LINK CHECKER

    def link_checker(self):
        self.reset_page(
            "🔗 FAKE LINK CHECKER",
            "संशयास्पद लिंक तपासा"
        )

        self.page.add_widget(
            self.label(
                "तपासण्यासाठी लिंक खाली पेस्ट करा.",
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
            "तपासणीचा निकाल येथे दिसेल.",
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
                result.text = "कृपया लिंक टाका."
                return

            if not re.match(r"^https?://", url, re.I):
                issues.append("http:// किंवा https:// नाही")

            if "@" in url:
                issues.append("लिंकमध्ये @ चिन्ह आहे")

            if re.search(
                r"(login|verify|gift|free-prize|password)",
                url,
                re.I
            ):
                issues.append("संशयास्पद शब्द आढळले")

            if re.match(
                r"^https?://\d{1,3}(?:\.\d{1,3}){3}",
                url,
                re.I
            ):
                issues.append("लिंक थेट IP address वापरते")

            if issues:
                result.text = "⚠️ सावधान!\n" + "\n".join(issues)

                self.log(
                    "Link Checker",
                    "Suspicious indicators found"
                )

            else:
                result.text = (
                    "ठळक धोक्याची चिन्हे आढळली नाहीत. "
                    "तरीही ही लिंक सुरक्षित असल्याची खात्री नाही."
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
            "ॲपमधील नोंदवलेल्या क्रिया"
        )

        try:
            with open(self.log_file, encoding="utf-8") as f:
                entries = json.load(f)

        except Exception:
            entries = []

        if not entries:
            self.page.add_widget(
                self.label(
                    "अजून कोणतीही नोंद नाही.",
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
            "मोबाईल सुरक्षा सूचना"
        )

        tips = [
            "✓ Android अपडेट ठेवा.",
            "✓ Google Play Protect सुरू ठेवा.",
            "✓ स्क्रीन लॉक आणि मजबूत PIN वापरा.",
            "✓ अनोळखी APK इन्स्टॉल करू नका.",
            "✓ महत्त्वाच्या फाइल्सचा बॅकअप ठेवा.",
            "✓ अनावश्यक ॲप परवानग्या बंद करा."
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
