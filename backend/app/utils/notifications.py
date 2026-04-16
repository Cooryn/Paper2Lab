from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.utils.files import ensure_dir, write_text


@dataclass
class NotificationMessage:
    title: str
    body: str


class Notifier:
    def notify(self, message: NotificationMessage) -> str:
        raise NotImplementedError


class ConsoleNotifier(Notifier):
    def notify(self, message: NotificationMessage) -> str:
        rendered = f"[{message.title}] {message.body}"
        print(rendered)
        return rendered


class MarkdownNotifier(Notifier):
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = ensure_dir(output_dir)

    def notify(self, message: NotificationMessage) -> str:
        path = self.output_dir / f"{message.title.lower().replace(' ', '_')}.md"
        write_text(path, f"# {message.title}\n\n{message.body}\n")
        return str(path)


class StubIntegrationNotifier(Notifier):
    def notify(self, message: NotificationMessage) -> str:
        return f"stub://{message.title}"

