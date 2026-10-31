"""Fail if a staged file contains a configured credential; never display its value."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
secrets = []
for line in (root / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" not in line or line.lstrip().startswith("#"):
        continue
    name, value = line.split("=", 1)
    if any(key in name.upper() for key in ("KEY", "DATABASE_URL", "TOKEN", "PASSWORD")):
        value = value.strip().strip("\"'")
        if value:
            secrets.append(value.encode())
paths = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=root).split(b"\0")
failed = False
for raw in filter(None, paths):
    path = raw.decode()
    if path == ".env" or path.startswith(".venv/") or "/node_modules/" in path:
        print(f"Forbidden staged path: {path}")
        failed = True
        continue
    result = subprocess.run(["git", "show", f":{path}"], cwd=root, capture_output=True)
    if result.returncode == 0 and any(secret in result.stdout for secret in secrets):
        print(f"Configured credential found in staged file: {path}")
        failed = True
print("Secret scan: FAIL" if failed else "Secret scan: PASS")
sys.exit(1 if failed else 0)
