#!/usr/bin/env python3
"""Create a business-specific confidence design package from bundled templates."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


TEMPLATE_MAP = {
    "confidence-contract.template.yaml": "confidence-contract.yaml",
    "known-risk-patterns.template.yaml": "known-risk-patterns.yaml",
    "validator-spec.template.yaml": "validator-spec.yaml",
    "confidence-review-report.template.md": "confidence-review-report.md",
}


def render_template(text: str, agent_id: str, agent_name: str) -> str:
    return text.replace("{{AGENT_ID}}", agent_id).replace("{{AGENT_NAME}}", agent_name)


def ensure_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()):
        if not force:
            raise FileExistsError(
                f"Target directory is not empty: {target}. Use --force to replace generated files."
            )
    target.mkdir(parents=True, exist_ok=True)


def scaffold(agent_id: str, agent_name: str, output: Path, force: bool = False) -> list[Path]:
    script_dir = Path(__file__).resolve().parent
    assets_dir = script_dir.parent / "assets"
    ensure_target(output, force)

    created: list[Path] = []
    for source_name, target_name in TEMPLATE_MAP.items():
        source = assets_dir / source_name
        if not source.exists():
            raise FileNotFoundError(f"Missing bundled template: {source}")
        target = output / target_name
        if target.exists() and not force:
            raise FileExistsError(f"Refusing to overwrite existing file: {target}")
        rendered = render_template(source.read_text(encoding="utf-8"), agent_id, agent_name)
        target.write_text(rendered, encoding="utf-8")
        created.append(target)

    validators_dir = output / "validators"
    tests_dir = output / "tests"
    validators_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    validator_file = validators_dir / "validate_replace_me.py"
    validator_content = '''#!/usr/bin/env python3
"""Replace this placeholder with a deterministic business validator."""


def validate(context: dict) -> dict:
    """Return the standard validation result structure."""
    raise NotImplementedError("Implement the business-specific validation logic")
'''
    if force or not validator_file.exists():
        validator_file.write_text(validator_content, encoding="utf-8")
        created.append(validator_file)

    test_file = tests_dir / "test_replace_me_risk.py"
    test_content = '''import unittest


class ReplaceMeRiskTest(unittest.TestCase):
    @unittest.skip("Replace with a regression test for the confirmed issue")
    def test_known_issue_is_detected(self) -> None:
        self.fail("Implement the regression test")


if __name__ == "__main__":
    unittest.main()
'''
    if force or not test_file.exists():
        test_file.write_text(test_content, encoding="utf-8")
        created.append(test_file)

    readme_file = output / "README.md"
    readme_content = f'''# {agent_name} 可信等级设计包

本目录由 `agent-confidence-designer` 脚手架生成。

1. 替换所有 `TODO`、`replace-me-*` 占位符；
2. 根据真实业务实现 `validators/`；
3. 将开发测试和用户自测问题写入 `known-risk-patterns.yaml`；
4. 为每个问题编写回归测试；
5. 运行设计校验脚本；
6. 由业务、开发和测试共同评审高可信条件。

Agent ID: `{agent_id}`
'''
    if force or not readme_file.exists():
        readme_file.write_text(readme_content, encoding="utf-8")
        created.append(readme_file)

    return created


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a business-specific confidence design package."
    )
    parser.add_argument("--agent-id", required=True, help="Stable lower-case agent identifier")
    parser.add_argument("--agent-name", required=True, help="Human-readable agent name")
    parser.add_argument("--output", required=True, type=Path, help="Target directory")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace generated files in an existing target directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        created = scaffold(args.agent_id, args.agent_name, args.output.resolve(), args.force)
    except (FileExistsError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"Created confidence design package at: {args.output.resolve()}")
    for path in created:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
