"""Dependency-free local documentation link and basic secret-pattern checks."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)|!\[[^]]*\]\(([^)]+)\)")
SECRET = re.compile(r"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sk-[A-Za-z0-9]{20,}")


def check() -> list[str]:
    errors = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "node_modules", "__pycache__", "dist", "build"}
                                         for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix not in {".md", ".py", ".json", ".toml", ".yml", ".mjs", ".mmd", ".svg"}:
            continue
        content = path.read_text(encoding="utf-8")
        if SECRET.search(content):
            errors.append(f"possible secret in {path.relative_to(ROOT)}")
        if path.suffix != ".md":
            continue
        for match in LINK.finditer(content):
            target = (match.group(1) or match.group(2)).split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).exists():
                errors.append(f"broken local link: {path.relative_to(ROOT)} -> {target}")
    return errors


if __name__ == "__main__":
    failures = check()
    print("\n".join(failures) if failures else "local links and basic secret patterns: OK")
    sys.exit(bool(failures))
