from __future__ import annotations

import json
from typing import Optional

from .tools import (
    handle_create_run,
    handle_status,
    handle_workflow_status,
    handle_list_inputs,
    handle_list_outputs,
    handle_read_output,
)

_HELP_TEXT = """\
/ai-pipeline — AI data analysis pipeline

Subcommands:
  run <file>               새 분석 런 생성 (CSV/Excel/JSON/TSV)
  status                   현재 런 상태 확인
  workflow [--run-id ID]   7단계 워크플로우 진행률
  inputs [--run-id ID]     등록된 소스 파일 목록
  outputs [--run-id ID]    생성된 출력 파일 목록
  read <name> [--run-id]   특정 출력 파일 내용 읽기
"""


def handle_slash(raw_args: str) -> Optional[str]:
    argv = raw_args.strip().split()
    if not argv or argv[0] in {"help", "-h", "--help"}:
        return _HELP_TEXT

    sub = argv[0]
    rest = argv[1:]

    def _fmt(result: dict) -> str:
        return json.dumps(result, ensure_ascii=False, indent=2)

    def _flag(flag: str, default: str = "") -> str:
        try:
            return rest[rest.index(flag) + 1]
        except (ValueError, IndexError):
            return default

    if sub == "run":
        if not rest:
            return "사용법: /ai-pipeline run <파일경로>"
        return _fmt(handle_create_run(path=rest[0], run_id=_flag("--run-id")))

    if sub == "status":
        return _fmt(handle_status())

    if sub == "workflow":
        return _fmt(handle_workflow_status(run_id=_flag("--run-id")))

    if sub == "inputs":
        return _fmt(handle_list_inputs(run_id=_flag("--run-id")))

    if sub == "outputs":
        return _fmt(handle_list_outputs(run_id=_flag("--run-id")))

    if sub == "read":
        if not rest:
            return "사용법: /ai-pipeline read <파일명>"
        return _fmt(handle_read_output(
            name=rest[0],
            run_id=_flag("--run-id"),
        ))

    return f"알 수 없는 서브커맨드: {sub}\n\n{_HELP_TEXT}"
