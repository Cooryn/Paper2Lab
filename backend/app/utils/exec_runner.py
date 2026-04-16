from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import BadRequestError
from app.utils.files import ensure_dir


logger = logging.getLogger("paper2lab.exec")


class ExecRunner:
    ALLOWED_PREFIXES = {
        "python": ["--version"],
        "pip": ["--version"],
        "Get-ChildItem": [],
        "cmd": ["/c", "dir"],
    }

    def __init__(self) -> None:
        self.settings = get_settings()
        self.log_path = ensure_dir(self.settings.log_dir) / "exec.log"

    def run(self, *, agent_name: str, command: list[str], cwd: Path) -> dict[str, str | int]:
        workspace_root = self.settings.backend_dir.parent.resolve()
        resolved_cwd = cwd.resolve()
        if workspace_root not in [resolved_cwd, *resolved_cwd.parents]:
            raise BadRequestError("Exec cwd must stay inside the workspace.")

        binary = command[0]
        if binary not in self.ALLOWED_PREFIXES:
            raise BadRequestError(f"Command '{binary}' is not allowed by ExecRunner.")

        allowed_args = self.ALLOWED_PREFIXES[binary]
        if allowed_args and command[1:] != allowed_args:
            raise BadRequestError(f"Arguments for '{binary}' are restricted.")

        logger.info("ExecRunner | agent=%s | cwd=%s | command=%s", agent_name, resolved_cwd, command)
        result = subprocess.run(
            command,
            cwd=resolved_cwd,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"agent={agent_name} cwd={resolved_cwd} command={' '.join(command)} "
                f"returncode={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}\n"
            )
        return {
            "command": " ".join(command),
            "cwd": str(resolved_cwd),
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

