import tempfile
from pathlib import Path

import pytest

from src import ROOT_DIR
from src.crypto.crypto import decrypt_base64_token, encrypt_bytes

ENCRYPTION_SDF_PATH: Path = ROOT_DIR.joinpath("tests/crypto/data")

# Collect SDF files once at import
SDF_FILES = list(ENCRYPTION_SDF_PATH.glob("*.sdf"))


@pytest.mark.parametrize(
    "case",
    list(enumerate(SDF_FILES)),
    ids=lambda p: f"<test:{p[0]}> {p[1].name}",
)
def test_sdf_encryption_roundtrip(case):
    """
    AES-GCM encrypt→decrypt→round-trip for each SDF file,
    using tempfile to isolate output artifacts.
    """
    idx, sdf_path = case
    password = "test-password"

    # Load original SDF content
    original_data = sdf_path.read_bytes()

    # Use a temporary directory for encrypted+decrypted artifacts
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        enc_path = tmpdir / f"{sdf_path.stem}.enc"
        dec_path = tmpdir / f"{sdf_path.stem}.sdf.dec"

        # Encrypt → produce base64 token
        token = encrypt_bytes(original_data, password)
        assert isinstance(token, str)
        assert token.strip() != ""

        # Save ciphertext so we behave like CLI (optional)
        enc_path.write_text(token, encoding="utf-8")

        # Read the ciphertext back (simulate round-trip file flow)
        loaded_token = enc_path.read_text(encoding="utf-8")

        # Decrypt
        decrypted = decrypt_base64_token(loaded_token, password)
        dec_path.write_bytes(decrypted)

        # Assert byte-level identity
        assert decrypted == original_data, f"SDF round-trip mismatch: {sdf_path}"

        # Additional sanity: decrypted file exists & matches size
        assert dec_path.is_file()
        assert dec_path.stat().st_size == len(original_data)
