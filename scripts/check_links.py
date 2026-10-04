"""Prueft Dokumentenlinks in allen Markdown-Dateien des Repositories."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Match Markdown links: [text](target) - ignore external http/https/mailto
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def check_file_links(repo_root: Path) -> list[str]:
    """Findet alle toten relativen Links in Markdown-Dateien."""
    errors: list[str] = []
    md_files = list(repo_root.glob("**/*.md"))

    for md_file in md_files:
        # Ignore virtual env or .git if present
        if ".venv" in md_file.parts or ".git" in md_file.parts:
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as err:
            errors.append(f"Konnte {md_file.relative_to(repo_root)} nicht lesen: {err}")
            continue

        for match in LINK_PATTERN.finditer(content):
            raw_target = match.group(2).strip()

            # Ignore external protocols and special schemes
            if raw_target.startswith(("http://", "https://", "mailto:", "conversation://")):
                continue

            # Strip optional anchor
            target_path_str = raw_target.split("#")[0].strip()
            if not target_path_str:
                # Same file anchor
                continue

            # Handle file:/// or relative path
            if target_path_str.startswith("file:///"):
                target_path_str = target_path_str[8:]

            target_path = Path(target_path_str)
            if not target_path.is_absolute():
                resolved = (md_file.parent / target_path).resolve()
            else:
                resolved = target_path.resolve()

            if not resolved.exists():
                rel_source = md_file.relative_to(repo_root)
                errors.append(f"{rel_source}: Linkziel '{raw_target}' existiert nicht ({resolved})")

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    errors = check_file_links(repo_root)
    if errors:
        sys.stderr.write(f"Gefundene Linkfehler ({len(errors)}):\n")
        for err in errors:
            sys.stderr.write(f"  - {err}\n")
        return 1

    sys.stdout.write("Alle Dokumentenlinks erfolgreich geprueft. Keine toten Links gefunden.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
