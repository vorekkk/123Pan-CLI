"""Maintain full command schemas and API mappings from the CLI source of truth."""

import argparse
import json
import os
import sys
from pathlib import Path

from pan123_cli.catalog import ENDPOINTS
from pan123_cli.cli import build_parser

os.environ["COLUMNS"] = "80"


def save(path, content):
    if "--check" in sys.argv:
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            raise SystemExit(
                f"Skill reference drift: {path.name}; run scripts/build_skill_reference.py"
            )
    else:
        path.write_text(content, encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "skills/pan123-cli/references"
coverage = json.loads((ROOT / "docs/API覆盖清单.json").read_text(encoding="utf-8"))
lines = [
    "# API 与 CLI 映射",
    "",
    "官方资料快照 2026-09-11；真实验证范围见各路由备注。此表由 catalog 自动生成。",
    "",
]
for endpoint in ENDPOINTS:
    lines += [
        f"## pan123 {' '.join(endpoint.command)}",
        "",
        f"`{endpoint.method} {endpoint.path}`，参数位置 `{endpoint.location}`；只读 `{endpoint.read_only}`；确认 `{endpoint.confirmation}`。",
        "",
    ]
    if endpoint.fixed:
        lines += [f"固定请求字段：`{json.dumps(dict(endpoint.fixed), ensure_ascii=False)}`", ""]
    if endpoint.wait:
        lines += [f"等待配置：`{json.dumps(dict(endpoint.wait), ensure_ascii=False)}`", ""]
    if endpoint.fields:
        lines += [
            "| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |",
            "|---|---|---|---|---|---|",
        ]
    for field in endpoint.fields:
        limits = {
            key: getattr(field, key)
            for key in ("choices", "minimum", "maximum", "max_items")
            if getattr(field, key) is not None
        }
        lines += [
            f"| {'--' + field.flag if field.flag else 'stdin / 流程注入'} | {field.wire} | {field.kind} | {field.required} | {field.default} | {json.dumps(limits, ensure_ascii=False)} |"
        ]
    for path in endpoint.source_paths:
        from urllib.parse import quote

        lines += [f"- [官方快照：{path}]({quote('api-source/' + path)})"]
    routes = [
        route
        for route in coverage["unique_api_routes"]
        if route["method"] == endpoint.method and route["path"] == endpoint.path
    ]
    for route in routes:
        lines += [
            f"真实验证：`{route.get('real_verification', 'not_verified')}`；{route.get('real_verification_blocker', '')}",
            "",
        ]
save(REF / "api-mapping.md", "\n".join(lines) + "\n")
# Parser help captures local/high-level commands and all exact option names.
helps = []


def visit(parser):
    helps.append("## " + parser.prog + "\n\n```text\n" + parser.format_help() + "```\n")
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for child in action.choices.values():
                visit(child)


visit(build_parser())
save(REF / "parser-help.md", "# 实际 CLI 帮助全集\n\n" + "\n".join(helps))
