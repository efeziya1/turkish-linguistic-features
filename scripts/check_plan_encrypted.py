"""pre-commit denetimi: staged `plan/` dosyaları git-crypt ile şifreli mi.

Why: git-crypt kurulu ya da açık (`git-crypt unlock`) olmayan makinede filtre
hiç çalışmaz ve dosya public depoya düz metin gider. Staged blob'un başlığına
bakar; git-crypt'in kurulu olmasını gerektirmez.
"""
from __future__ import annotations

import subprocess
import sys

GITCRYPT_HEADER = b"\x00GITCRYPT\x00"


def is_staged_encrypted(path: str) -> bool:
    blob = subprocess.run(["git", "show", f":{path}"], capture_output=True, check=True).stdout
    return blob.startswith(GITCRYPT_HEADER)


plaintext = [path for path in sys.argv[1:] if not is_staged_encrypted(path)]
if plaintext:
    print("Şifrelenmemiş plan dosyası — önce `git-crypt unlock <anahtar-dosyası>`, sonra yeniden `git add`:")
    print("\n".join(f"  {path}" for path in plaintext))
    sys.exit(1)
