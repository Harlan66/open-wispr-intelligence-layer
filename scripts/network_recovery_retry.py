#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OPENCLAW_BIN = "/opt/homebrew/bin/openclaw"
RUN_ENV = dict(os.environ)
RUN_ENV["PATH"] = "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
LOG_PREFIX = "[network-recovery-retry]"


def utc_now() -> float:
    return time.time()


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    print(f"{ts} {LOG_PREFIX} {msg}")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def network_ready() -> bool:
    for host, port in [("1.1.1.1", 443), ("8.8.8.8", 53)]:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            continue
    return False


def pending_mtime(path_str: str) -> float:
    p = Path(path_str).expanduser()
    if not p.exists() or p.stat().st_size == 0:
        return 0.0
    return p.stat().st_mtime


def run_job(job_id: str, timeout_ms: int, expect_final: bool) -> tuple[bool, str]:
    cmd = [OPENCLAW_BIN, "cron", "run", job_id, "--timeout", str(timeout_ms)]
    if expect_final:
        cmd.append("--expect-final")
    proc = subprocess.run(cmd, capture_output=True, text=True, env=RUN_ENV)
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    ok = proc.returncode == 0
    try:
        parsed = json.loads(out)
        if parsed.get("ok") is True and parsed.get("reason") in {"already-running", None}:
            ok = True
    except Exception:
        pass
    return ok, out[-4000:]


def main() -> int:
    parser_config = os.environ.get("OWHR_CONFIG", "./config/network_recovery_retry.example.json")
    state_path = Path(os.environ.get("OWHR_STATE", str(Path.home() / ".config" / "open-wispr" / "network-recovery-state.json")))
    cfg = load_json(Path(parser_config), {"tasks": []})
    state = load_json(state_path, {"tasks": {}})
    state.setdefault("tasks", {})

    if not network_ready():
        log("network not ready; skip")
        save_json(state_path, state)
        return 0

    for task in cfg.get("tasks", []):
        if not task.get("enabled", True):
            continue
        name = str(task["name"])
        job_id = str(task["jobId"])
        timeout_ms = int(task.get("timeoutMs", 300000))
        cooldown = int(task.get("cooldownSeconds", 600))
        expect_final = bool(task.get("expectFinal", True))
        p_mtime = pending_mtime(str(task["pendingPath"]))
        tstate = state["tasks"].setdefault(name, {})
        last_success_input_mtime = float(tstate.get("lastSuccessInputMtime", 0.0))
        last_attempt = float(tstate.get("lastAttemptAt", 0.0))

        if p_mtime == 0.0 or p_mtime <= last_success_input_mtime or utc_now() - last_attempt < cooldown:
            continue

        log(f"retrying task={name} jobId={job_id}")
        tstate["lastAttemptAt"] = utc_now()
        ok, output = run_job(job_id, timeout_ms, expect_final)
        tstate["lastOutputTail"] = output
        if ok:
            tstate["lastSuccessAt"] = utc_now()
            tstate["lastSuccessInputMtime"] = p_mtime
            log(f"task={name} success")
        else:
            tstate["lastErrorAt"] = utc_now()
            log(f"task={name} failed")

    save_json(state_path, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#huanyuan
