#!/usr/bin/env python3
"""Statically list target paths implied by the subset of chezmoi naming used here."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1] / "dotfiles"
special_prefixes = (".chezmoi", "run_")

def decode(part: str) -> str:
    for prefix in ("private_", "readonly_", "executable_", "create_", "modify_"):
        if part.startswith(prefix):
            part = part[len(prefix):]
    if part.startswith("dot_"):
        part = "." + part[4:]
    if part.endswith(".tmpl"):
        part = part[:-5]
    return part

targets = {}
for source in sorted(p for p in root.rglob("*") if p.is_file()):
    rel = source.relative_to(root)
    if rel.parts[0].startswith(special_prefixes) or rel.name.startswith(special_prefixes):
        continue
    target = Path(*(decode(part) for part in rel.parts))
    key = str(target)
    if key in targets:
        print(f"duplicate target: {key}: {targets[key]} and {rel}", file=sys.stderr)
        raise SystemExit(1)
    targets[key] = str(rel)
for target, source in sorted(targets.items()):
    print(f"{target}\t{source}")
