"""
MBCrypto - AES-256-GCM based helper for encrypting/decrypting secrets / files.

Features:
- Password-based key derivation via PBKDF2-HMAC-SHA256.
- AES-256-GCM authenticated encryption.
- Base64-encoded ciphertext (salt + nonce + ciphertext).
- CLI with Click, supporting:
    - encrypt [--name NAME] [INPUT_FILE] [OUTPUT_FILE]
    - decrypt [INPUT_FILE] [OUTPUT_FILE]
    - stdin fallback when INPUT_FILE not provided or omitted.
"""

import base64
import datetime
import os
import secrets
from typing import Optional

import click
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
NONCE_SIZE = 12
PBKDF2_ITERATIONS = 600_000


# ==== Core crypto helpers =====================================================


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from password and salt using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(plaintext: bytes, password: str) -> str:
    """
    Encrypt plaintext bytes using AES-256-GCM with PBKDF2-derived key.

    Returns:
        Base64-encoded string containing salt + nonce + ciphertext.
    """
    salt = secrets.token_bytes(SALT_SIZE)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    token_bytes = salt + nonce + ciphertext
    return base64.b64encode(token_bytes).decode("ascii")


def decrypt_base64_token(b64_token: str, password: str) -> bytes:
    """
    Decrypt a base64-encoded token produced by encrypt_bytes.

    Args:
        b64_token: base64 string of salt + nonce + ciphertext.
        password:  password used during encryption.

    Returns:
        Decrypted plaintext bytes.

    Raises:
        ValueError on invalid base64 or corrupted data.
        InvalidTag on wrong password or tampered ciphertext.
    """
    token_bytes = b"".join(b64_token.encode("utf-8").split())  # strip all whitespace

    try:
        data = base64.b64decode(token_bytes)
    except Exception as exc:
        raise ValueError("Input is not valid base64.") from exc

    if len(data) < SALT_SIZE + NONCE_SIZE:
        raise ValueError("Encrypted data too short / corrupted.")

    salt = data[:SALT_SIZE]
    nonce = data[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
    ciphertext = data[SALT_SIZE + NONCE_SIZE :]

    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


# ==== Core CLI logic (no Click decorators here) ===============================


def _read_plaintext_from_source(input_file: Optional[str]) -> bytes:
    """Read plaintext from file if given and exists, otherwise from stdin."""
    if input_file and os.path.isfile(input_file):
        with open(input_file, "rb") as f:
            return f.read()

    stdin = click.get_text_stream("stdin")
    if stdin.isatty():
        click.echo("Enter/paste your secret below, then press Ctrl+D:")

    data = stdin.read()
    if not data:
        raise click.ClickException("No input received.")
    return data.encode("utf-8")


def _read_token_from_source(input_file: Optional[str]) -> str:
    """Read base64 token from file if given and exists, otherwise from stdin."""
    if input_file and os.path.isfile(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            return f.read()

    stdin = click.get_text_stream("stdin")
    if stdin.isatty():
        click.echo("Enter/paste encrypted base64 text below, then press Ctrl+D:")

    token_str = stdin.read()
    if not token_str:
        raise click.ClickException("No input received.")
    return token_str


def _determine_encrypt_out_path(
    name: Optional[str], input_file: Optional[str], output_file: Optional[str]
) -> str:
    if output_file:
        return output_file
    if name:
        return f"encrypted_{name}.enc"
    # fallback timestamp-based name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"encrypted_{timestamp}.enc"


def _determine_decrypt_out_path(output_file: Optional[str]) -> str:
    if output_file:
        return output_file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"decrypted_{timestamp}.dec"


def encrypt_core(
    name: Optional[str], input_file: Optional[str], output_file: Optional[str]
) -> None:
    """Core encryption logic: used by both 'encrypt' subcommand and legacy mode."""
    plaintext = _read_plaintext_from_source(input_file)

    password = click.prompt(
        "Password", hide_input=True, confirmation_prompt=True, type=str
    )

    b64_token = encrypt_bytes(plaintext, password)
    out_path = _determine_encrypt_out_path(name, input_file, output_file)

    # Write base64 token as text
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(b64_token)

    click.echo(
        f"Encrypted -> {out_path}\n"
        "(Cipher: AES-256-GCM, key derived via PBKDF2-HMAC-SHA256)\n"
        "(Base64-encoded ciphertext)\n"
    )
    click.echo(b64_token)


def decrypt_core(input_file: Optional[str], output_file: Optional[str]) -> None:
    """Core decryption logic: used by 'decrypt' subcommand."""
    b64_token = _read_token_from_source(input_file)
    password = click.prompt("Password", hide_input=True, type=str)

    try:
        plaintext = decrypt_base64_token(b64_token, password)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    except InvalidTag:
        raise click.ClickException(
            "Decryption failed. Wrong password or corrupted data."
        )

    out_path = _determine_decrypt_out_path(output_file)

    # Write plaintext to file for safety / tooling
    with open(out_path, "wb") as f:
        f.write(plaintext)

    click.echo(f"Decrypted -> {out_path}\nSecret content:\n")
    try:
        click.echo(plaintext.decode("utf-8"))
    except UnicodeDecodeError:
        click.echo("<binary data>", err=True)


# ==== Click CLI ===============================================================


@click.group()
def mbcrypto() -> None:
    """
    MBCrypto - encrypt/decrypt secrets using AES-256-GCM.

    Usage:
        MBCrypto encrypt [--name NAME] [INPUT_FILE] [OUTPUT_FILE]
        MBCrypto decrypt [INPUT_FILE] [OUTPUT_FILE]
    """
    pass


@mbcrypto.command(name="encrypt")
@click.option(
    "--name",
    "-n",
    "name",
    default=None,
    help="Logical name for the encrypted output (encrypted_<name>.enc).",
)
@click.argument("input_file", required=False)
@click.argument("output_file", required=False)
def encrypt_cmd(
    name: Optional[str], input_file: Optional[str], output_file: Optional[str]
) -> None:
    """Encrypt secret data (file or stdin) into a base64-encoded ciphertext."""
    encrypt_core(name=name, input_file=input_file, output_file=output_file)


@mbcrypto.command(name="decrypt")
@click.argument("input_file", required=False)
@click.argument("output_file", required=False)
def decrypt_cmd(input_file: Optional[str], output_file: Optional[str]) -> None:
    """Decrypt a base64-encoded ciphertext and output the plaintext."""
    decrypt_core(input_file=input_file, output_file=output_file)


def main() -> None:
    """Entry point for console_scripts or python -m usage."""
    mbcrypto(prog_name="MBCrypto")


if __name__ == "__main__":
    main()
