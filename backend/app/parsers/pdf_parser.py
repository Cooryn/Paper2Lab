from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader


class ParsedPaperContent(dict):
    pass


class PaperParser:
    def parse(self, pdf_path: Path) -> ParsedPaperContent:
        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages[:5])
        normalized = re.sub(r"\s+", " ", text).strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        title = lines[0] if lines else pdf_path.stem
        abstract = ""
        sections: list[str] = []
        abstract_match = re.search(r"abstract[:\s]+(.+?)(introduction|1\.|keywords)", normalized, re.I)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
        for line in lines:
            if len(line) < 120 and re.match(r"^(\d+\.|abstract|introduction|method|experiments|conclusion)", line, re.I):
                sections.append(line)

        return ParsedPaperContent(
            title=title,
            abstract=abstract or normalized[:900],
            sections=sections[:12],
            raw_text=normalized[:8000],
        )

