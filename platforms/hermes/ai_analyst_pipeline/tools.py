from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent
SCRIPT = PLUGIN_DIR / "scripts" / "ai_pipeline.py"
if not SCRIPT.exists():
    # Development checkout layout: shared runtime script lives at repo/shared/scripts.
    SCRIPT = PLUGIN_DIR.parents[2] / "shared" / "scripts" / "ai_pipeline.py"


def _run(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"success": True, "output": result.stdout}
    return {"success": False, "error": result.stderr or "no output"}


# ── schemas ──────────────────────────────────────────────────────────────────

AI_PIPELINE_CREATE_RUN_SCHEMA = {
    "name": "ai_pipeline_create_run",
    "description": "Create a new analysis run for a data file (CSV, Excel, JSON, TSV, PDF).",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Absolute path to the data file"},
            "run_id": {"type": "string", "description": "Optional run ID (auto-generated if omitted)"},
        },
        "required": ["path"],
    },
}

AI_PIPELINE_STATUS_SCHEMA = {
    "name": "ai_pipeline_status",
    "description": "Show current runtime status and latest run ID.",
    "parameters": {"type": "object", "properties": {}, "required": []},
}

AI_PIPELINE_WORKFLOW_STATUS_SCHEMA = {
    "name": "ai_pipeline_workflow_status",
    "description": "Show 7-step workflow progress for a run.",
    "parameters": {
        "type": "object",
        "properties": {
            "run_id": {"type": "string", "description": "Run ID (uses latest if omitted)"},
        },
        "required": [],
    },
}

AI_PIPELINE_LIST_INPUTS_SCHEMA = {
    "name": "ai_pipeline_list_inputs",
    "description": "List source files registered on a run.",
    "parameters": {
        "type": "object",
        "properties": {
            "run_id": {"type": "string", "description": "Run ID (uses latest if omitted)"},
        },
        "required": [],
    },
}

AI_PIPELINE_LIST_OUTPUTS_SCHEMA = {
    "name": "ai_pipeline_list_outputs",
    "description": "List output files produced by a run.",
    "parameters": {
        "type": "object",
        "properties": {
            "run_id": {"type": "string", "description": "Run ID (uses latest if omitted)"},
        },
        "required": [],
    },
}

AI_PIPELINE_READ_OUTPUT_SCHEMA = {
    "name": "ai_pipeline_read_output",
    "description": "Read the content of a specific output file from a run.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Output file name (e.g. 07_executive_report.md)"},
            "run_id": {"type": "string", "description": "Run ID (uses latest if omitted)"},
            "max_chars": {"type": "integer", "description": "Max characters to return (default 20000)"},
        },
        "required": ["name"],
    },
}

AI_PIPELINE_WRITE_PROGRESS_SCHEMA = {
    "name": "ai_pipeline_write_progress",
    "description": "Update the pipeline progress status for a run.",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["pending", "running", "complete", "failed"]},
            "current_step": {"type": "integer", "description": "Current step number (0-7)"},
            "run_id": {"type": "string"},
            "error": {"type": "string"},
        },
        "required": ["status"],
    },
}


# ── handlers ─────────────────────────────────────────────────────────────────

def handle_create_run(path: str, run_id: str = "", **kwargs) -> dict:
    args = ["create-run", "--path", path]
    if run_id:
        args += ["--run-id", run_id]
    return _run(*args)


def handle_status(**kwargs) -> dict:
    return _run("status")


def handle_workflow_status(run_id: str = "", **kwargs) -> dict:
    args = ["workflow-status", "--format", "json"]
    if run_id:
        args += ["--run-id", run_id]
    return _run(*args)


def handle_list_inputs(run_id: str = "", **kwargs) -> dict:
    args = ["list-inputs"]
    if run_id:
        args += ["--run-id", run_id]
    return _run(*args)


def handle_list_outputs(run_id: str = "", **kwargs) -> dict:
    args = ["list-outputs"]
    if run_id:
        args += ["--run-id", run_id]
    return _run(*args)


def handle_read_output(name: str, run_id: str = "", max_chars: int = 20000, **kwargs) -> dict:
    args = ["read-output", "--name", name, "--max-chars", str(max_chars)]
    if run_id:
        args += ["--run-id", run_id]
    return _run(*args)


def handle_write_progress(status: str, current_step: int = 0, run_id: str = "", error: str = "", **kwargs) -> dict:
    args = ["write-progress", "--status", status, "--current-step", str(current_step)]
    if run_id:
        args += ["--run-id", run_id]
    if error:
        args += ["--error", error]
    return _run(*args)
