#!/usr/bin/env python3
"""Create a business-specific confidence design package from templates."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE_MAP = {
    "confidence-contract.template.yaml": "confidence-contract.yaml",
    "known-risk-patterns.template.yaml": "known-risk-patterns.yaml",
    "confidence-logic.template.yaml": "confidence-logic.yaml",
    "confidence-review-report.template.md": "confidence-review-report.md",
}


def scaffold(agent_id: str, agent_name: str, output: Path, force: bool = False) -> list[Path]:
    assets = Path(__file__).resolve().parent.parent / "assets"
    if output.exists() and any(output.iterdir()) and not force:
        raise FileExistsError(f"Target directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for source_name, target_name in TEMPLATE_MAP.items():
        text = (assets / source_name).read_text(encoding="utf-8")
        text = text.replace("{{AGENT_ID}}", agent_id).replace("{{AGENT_NAME}}", agent_name)
        target = output / target_name
        if target.exists() and not force:
            raise FileExistsError(f"Refusing to overwrite: {target}")
        target.write_text(text, encoding="utf-8")
        created.append(target)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a confidence design package")
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        created = scaffold(args.agent_id, args.agent_name, args.output.resolve(), args.force)
    except FileExistsError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Created: {args.output.resolve()}")
    for path in created:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
