from __future__ import annotations

from pathlib import Path

from app.utils.files import GENERATOR_BANNER, write_text


def write_markdown(path: Path, body: str) -> Path:
    content = f"<!-- {GENERATOR_BANNER} -->\n\n{body.strip()}\n"
    return write_text(path, content)

