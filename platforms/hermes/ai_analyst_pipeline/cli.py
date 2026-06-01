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
    SCRIPT,
)

_HELP_TEXT = """\
/ai-pipeline — AI data analysis pipeline

Subcommands:
  run <file>               7단계 AI 분석 실행 지시 생성 (CSV/Excel/JSON/TSV)
  create-run <file>        새 분석 런만 생성
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

    # UX shortcut: allow `/ai-pipeline /path/to/file.csv` as an alias for
    # `/ai-pipeline run /path/to/file.csv`.
    if argv[0] not in {"run", "create-run", "status", "workflow", "inputs", "outputs", "read"}:
        argv = ["run", *argv]

    sub = argv[0]
    rest = argv[1:]

    def _fmt(result: dict) -> str:
        return json.dumps(result, ensure_ascii=False, indent=2)

    def _flag(flag: str, default: str = "") -> str:
        try:
            return rest[rest.index(flag) + 1]
        except (ValueError, IndexError):
            return default

    def _analysis_prompt(result: dict) -> str:
        run_id = result["run_id"]
        output_dir = result["output_dir"]
        source_files = result.get("source_files") or []
        source_path = source_files[0].get("path") if source_files else ""
        script_path = str(SCRIPT)
        return f"""AI analyst pipeline run created.

Run ID: {run_id}
Source: {source_path}
Output dir: {output_dir}

이제 이 메시지를 일반 답변으로 끝내지 말고, 즉시 아래 작업을 계속 수행하세요.

작업 지시:
1. ai-analyst-pipeline 스킬의 7단계 절차를 따른다.
2. run_id `{run_id}`를 사용한다.
3. source file `{source_path}`만 데이터 근거로 사용한다.
4. 각 단계 시작 전 progress를 running/current_step으로 갱신한다.
5. 산출물은 반드시 `{output_dir}` 아래에 생성한다.
6. 필요한 계산과 검증은 Python/pandas로 수행한다.
7. 단, Markdown 리포트·문제정의·인사이트·임원요약은 Python 템플릿으로 찍어내지 말고, 에이전트가 데이터와 계산 결과를 직접 검토해 작성한다.
8. 아래 산출물을 순서대로 모두 만든다:
   - 00_data_contract.md
   - 01_dataset_profile.md
   - 02_analysis_plan.md
   - 02_eda_report.md
   - 03_problem_definition.md
   - 04_kpi_summary.md
   - 04_metrics.json
   - 05_analysis.py
   - 05_analysis.ipynb
   - 05_analysis_report.md
   - 06_dashboard.html
   - 07_executive_report.md
   - 08_validation_report.md
9. 모든 산출물이 존재하고 비어 있지 않은지 확인한다.
10. 마지막에 `python3 {script_path} write-progress --status complete --current-step 7 --run-id {run_id}`를 실행하고 `python3 {script_path} validate-outputs --run-id {run_id}`로 검증한다.
11. validate 결과가 complete일 때만 사용자에게 완료 보고한다.
"""

    if sub == "run":
        if not rest:
            return "사용법: /ai-pipeline <파일경로> 또는 /ai-pipeline run <파일경로>"
        result = handle_create_run(path=rest[0], run_id=_flag("--run-id"))
        if not result.get("success", True):
            return _fmt(result)
        return _analysis_prompt(result)

    if sub == "create-run":
        if not rest:
            return "사용법: /ai-pipeline create-run <파일경로>"
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
