import tempfile
from pathlib import Path

import pytest

from src.crypto.crypto import decrypt_base64_token, encrypt_bytes

TEST_CASES = [
    {
        "label": "single_line",
        "plaintext": "mysuppoerpassword123",
    },
    {
        "label": "multi_line",
        "plaintext": "mysuppoerpassword123\nsecond line\nthird line",
    },
    {
        "label": "leading_trailing_ws",
        "plaintext": "   secret with spaces   \n  and tabs\t  ",
    },
    {
        "label": "unicode_emoji",
        "plaintext": "🔐 secret_key = 🔑\n😀😎🔥",
    },
    {
        "label": "unicode_multilingual",
        "plaintext": "秘密 ключ parola كلمة سر סוד\n第二行",
    },
    {
        "label": "long_secret",
        "plaintext": "X" * 5000,  # 5 KB payload
    },
]


def case_params():
    return pytest.mark.parametrize(
        "case",
        list(enumerate(TEST_CASES)),
        ids=lambda p: f"<test:{p[0]}> {p[1]['label']}",
    )


@case_params()
def test_core_roundtrip_string(case):
    _, payload = case
    plaintext = payload["plaintext"]
    password = "test-password"

    token = encrypt_bytes(plaintext.encode("utf-8"), password)

    assert isinstance(token, str)
    assert token.strip() != ""

    decrypted_bytes = decrypt_base64_token(token, password)
    decrypted = decrypted_bytes.decode("utf-8")

    assert decrypted == plaintext


@case_params()
def test_core_roundtrip_file(case):
    _, payload = case
    plaintext = payload["plaintext"]
    password = "test-password"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        plain_file = tmpdir_path / "secret.txt"
        plain_file.write_text(plaintext, encoding="utf-8")

        # encrypt file contents
        token = encrypt_bytes(plain_file.read_bytes(), password)

        enc_file = tmpdir_path / "secret.enc"
        enc_file.write_text(token, encoding="utf-8")

        loaded_token = enc_file.read_text(encoding="utf-8")
        decrypted_bytes = decrypt_base64_token(loaded_token, password)
        decrypted = decrypted_bytes.decode("utf-8")

        assert decrypted == plaintext
