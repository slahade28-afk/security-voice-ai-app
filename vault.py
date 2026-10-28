import os
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken


def make_key(pin, salt):
    key = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt,
        600000
    )
    return base64.urlsafe_b64encode(key)


def encrypt_file(file_path, pin):
    file_path = Path(file_path)

    salt = os.urandom(16)
    key = make_key(pin, salt)
    cipher = Fernet(key)

    with open(file_path, "rb") as file:
        data = file.read()

    encrypted_data = cipher.encrypt(data)

    vault_path = file_path.with_suffix(
        file_path.suffix + ".vault"
    )

    with open(vault_path, "wb") as file:
        file.write(b"SV01" + salt + encrypted_data)

    return str(vault_path)


def decrypt_file(vault_path, pin):
    vault_path = Path(vault_path)

    with open(vault_path, "rb") as file:
        data = file.read()

    if not data.startswith(b"SV01"):
        raise ValueError("ही Vault फाइल योग्य नाही.")

    salt = data[4:20]
    encrypted_data = data[20:]

    key = make_key(pin, salt)

    try:
        decrypted_data = Fernet(key).decrypt(encrypted_data)
    except InvalidToken:
        raise ValueError("PIN चुकीचा आहे किंवा फाइल खराब आहे.")

    output_path = vault_path.with_suffix("")

    with open(output_path, "xb") as file:
        file.write(decrypted_data)

    return str(output_path)
