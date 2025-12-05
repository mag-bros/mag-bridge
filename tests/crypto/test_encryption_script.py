from pathlib import Path

import pytest
from click.testing import CliRunner

import src.crypto.crypto as mbmod
from src.crypto.crypto import decrypt_base64_token, encrypt_bytes, mbcrypto


def test_core_roundtrip_string():
    plaintext = "mysuppoerpassword123\nsecond line"
    password = "test-password"

    # --- Act: encrypt to base64 token ---
    token = encrypt_bytes(plaintext.encode("utf-8"), password)

    # sanity: token is non-empty and looks like base64 (no whitespace)
    assert isinstance(token, str)
    assert token.strip() != ""
    assert "\n" not in token

    # --- Act: decrypt back ---
    decrypted_bytes = decrypt_base64_token(token, password)
    decrypted = decrypted_bytes.decode("utf-8")

    # --- Assert ---
    assert decrypted == plaintext


def test_core_roundtrip_file(tmp_path: Path):
    plaintext = "mysuppoerpassword123\nsecond line"
    password = "test-password"

    plain_file = tmp_path / "secret.txt"
    plain_file.write_text(plaintext, encoding="utf-8")

    # encrypt file contents via core API
    token = encrypt_bytes(plain_file.read_bytes(), password)

    # simulate storing token in a file like the CLI does
    enc_file = tmp_path / "secret.enc"
    enc_file.write_text(token, encoding="utf-8")

    # read back and decrypt via core API
    loaded_token = enc_file.read_text(encoding="utf-8")
    decrypted_bytes = decrypt_base64_token(loaded_token, password)
    decrypted = decrypted_bytes.decode("utf-8")

    assert decrypted == plaintext
