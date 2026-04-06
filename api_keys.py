"""
api_keys.py — Secure API key retrieval.

Keys are stored in the OS credential manager (Windows Credential Manager,
macOS Keychain, or Linux Secret Service) — never in plain-text files.

To store your key, run once in a terminal:
    python -c "import keyring; keyring.set_password('openrouter', 'api_key', 'sk-or-v1-...')"
"""

import keyring


def get_api_key() -> str:
    """
    Retrieves the OpenRouter API key from the OS credential store.
    Raises ValueError if the key is missing or malformed.
    """
    try:
        key = keyring.get_password("openrouter", "api_key")
        if key and key.startswith("sk-or-v1-"):
            return key.strip()
    except Exception as e:
        raise RuntimeError(f"Could not access the OS credential store: {e}") from e

    raise ValueError(
        "\n\n❌  OpenRouter API key not found in the credential store.\n"
        "    Run this once to store it:\n\n"
        "    python -c \"import keyring; "
        "keyring.set_password('openrouter', 'api_key', 'sk-or-v1-YOUR_KEY')\"\n"
    )
