"""Run real browser persistence checks in a dedicated, disposable Neon schema."""
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

from sqlalchemy import text

from app.config import ROOT
from app.db import engine
from app.models import Base


def wait_ready(url):
    for _ in range(60):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.5)
    raise RuntimeError("Isolated browser test service did not start; inspect ignored acceptance logs")


def main():
    schema = "sdr_e2e_" + uuid.uuid4().hex
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required")
    processes = []
    logs = []
    try:
        with engine.begin() as db:
            db.execute(text(f'CREATE SCHEMA "{schema}"'))
            Base.metadata.create_all(db.execution_options(schema_translate_map={"sdr": schema}))
        env = {**os.environ, "APP_ENV": "test", "SDR_TEST_SCHEMA": schema,
               "BACKEND_URL": "http://127.0.0.1:8001", "E2E_BASE_URL": "http://127.0.0.1:5174",
               "ISOLATED_E2E": "1"}
        commands = [([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
                     ROOT / "backend", "acceptance-backend.log"),
                    ([sys.executable, "-m", "app.worker"], ROOT / "backend", "acceptance-worker.log"),
                    ([node, str(ROOT / "frontend/node_modules/vite/bin/vite.js"), "--host", "127.0.0.1", "--port", "5174"],
                     ROOT / "frontend", "acceptance-frontend.log")]
        for command, cwd, filename in commands:
            log = (artifacts / filename).open("w", encoding="utf-8")
            logs.append(log)
            processes.append(subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=log,
                                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0))
        wait_ready("http://127.0.0.1:8001/api/health")
        wait_ready("http://127.0.0.1:5174")
        test_files = sys.argv[1:] or ["tests/e2e/prospects-persistence.spec.ts"]
        result = subprocess.run([node, str(ROOT / "frontend/node_modules/@playwright/test/cli.js"),
                                 "test", *test_files], cwd=ROOT / "frontend", env=env,
                                check=False)
        return result.returncode
    finally:
        for process in processes:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for log in logs:
            log.close()
        if not re.fullmatch(r"sdr_e2e_[a-f0-9]{32}", schema):
            raise RuntimeError("Refusing cleanup of an unexpected schema")
        with engine.begin() as db:
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        print("Isolated acceptance schema cleaned; normal application data untouched.")


if __name__ == "__main__":
    sys.exit(main())
