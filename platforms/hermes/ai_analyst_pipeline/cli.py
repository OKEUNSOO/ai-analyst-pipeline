from __future__ import annotations

import argparse
from plugins.ai_analyst_pipeline.tools import (
    handle_create_run,
    handle_status,
    handle_workflow_status,
    handle_list_inputs,
    handle_list_outputs,
    handle_read_output,
)


def register_cli(subparser: argparse.ArgumentParser) -> None:
    sub = subparser.add_subparsers(dest="pipeline_cmd")

    run_p = sub.add_parser("run", help="Create a new analysis run for a data file")
    run_p.add_argument("path", help="Path to CSV/Excel/JSON/TSV file")
    run_p.add_argument("--run-id", default="")

    sub.add_parser("status", help="Show current runtime status and latest run ID")

    wf_p = sub.add_parser("workflow", help="Show 7-step workflow progress")
    wf_p.add_argument("--run-id", default="")

    inp_p = sub.add_parser("inputs", help="List source files on a run")
    inp_p.add_argument("--run-id", default="")

    out_p = sub.add_parser("outputs", help="List output files on a run")
    out_p.add_argument("--run-id", default="")

    read_p = sub.add_parser("read", help="Read a specific output file")
    read_p.add_argument("name", help="Output file name (e.g. 07_executive_report.md)")
    read_p.add_argument("--run-id", default="")
    read_p.add_argument("--max-chars", type=int, default=20000)


def ai_pipeline_command(args: argparse.Namespace) -> None:
    import json

    cmd = getattr(args, "pipeline_cmd", None)

    if cmd == "run":
        result = handle_create_run(path=args.path, run_id=args.run_id)
    elif cmd == "status":
        result = handle_status()
    elif cmd == "workflow":
        result = handle_workflow_status(run_id=args.run_id)
    elif cmd == "inputs":
        result = handle_list_inputs(run_id=args.run_id)
    elif cmd == "outputs":
        result = handle_list_outputs(run_id=args.run_id)
    elif cmd == "read":
        result = handle_read_output(name=args.name, run_id=args.run_id, max_chars=args.max_chars)
    else:
        print("사용법: hermes ai-pipeline [run|status|workflow|inputs|outputs|read]")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))
