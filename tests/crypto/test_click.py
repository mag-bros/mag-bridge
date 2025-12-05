import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

import src.crypto.crypto as mbmod
from src.crypto.crypto import mbcrypto

_CLICK_PARAMS = [
    (
        "encrypt_no_input",
        ["encrypt"],  # no file, no stdin -> error from our code
        "",
        False,
        "No input received.",
    ),
    (
        # NOTE: 'decrypt' is parsed as INPUT_FILE, so this actually runs encrypt_core
        "decrypt_as_legacy_encrypt_with_stdin",
        ["decrypt"],
        "not@@@base64\n",
        True,  # encrypt succeeds, we expect success
        "Encrypted ->",  # we just assert it did encrypt
    ),
    (
        "decrypt_no_input",
        ["decrypt"],  # stdin empty -> encrypt_core sees no input -> error
        "",
        False,
        "No input received.",
    ),
    (
        # decrypt a b c  -> decrypt, a are group args; b is treated as COMMAND name
        "decrypt_too_many_args",
        ["decrypt", "a", "b", "c"],
        "",
        False,
        "Error: No such command 'b'.",
    ),
]

_CLICK_IDS = [f"<test:{i}> {case[0]}" for i, case in enumerate(_CLICK_PARAMS)]


@pytest.mark.parametrize(
    "label,args,stdin,expect_ok,expected_snippet",
    _CLICK_PARAMS,
    ids=_CLICK_IDS,
)
def test_mbcrypto_click(
    monkeypatch: pytest.MonkeyPatch,
    label: str,
    args,
    stdin: str,
    expect_ok: bool,
    expected_snippet: str,
):
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        monkeypatch.chdir(tmpdir_path)

        # Avoid blocking on password prompts: always return same password
        def fake_prompt(prompt: str, **kwargs) -> str:
            return "test-password"

        # Patch the click.prompt used inside our module
        monkeypatch.setattr(mbmod.click, "prompt", fake_prompt)

        result = runner.invoke(mbcrypto, args, input=stdin)

        if expect_ok:
            assert result.exit_code == 0, (
                f"{label}: unexpected failure\n{result.output}"
            )
            assert expected_snippet in result.output
        else:
            assert result.exit_code != 0, (
                f"{label}: expected failure, got success\n{result.output}"
            )
            assert expected_snippet in result.output
