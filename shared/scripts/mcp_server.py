#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

os.environ.setdefault("AI_PIPELINE_RUNTIME_ROOT", str((SCRIPT_DIR.parent / "data-ai-pipeline").resolve()))

import ai_pipeline
from mcp.server.fastmcp import FastMCP


def set_runtime_root(path: str | None = None) -> dict[str, Any]:
    if not path:
        resolved = Path(os.environ.get("AI_PIPELINE_RUNTIME_ROOT", str((SCRIPT_DIR.parent / "data-ai-pipeline").resolve())).strip()).expanduser().resolve()
        return {"runtime_root": str(resolved)}
    resolved = Path(path).expanduser().resolve()
    os.environ["AI_PIPELINE_RUNTIME_ROOT"] = str(resolved)
    return {"runtime_root": str(resolved)}


def _to_source_paths(path: str | None = None, source_paths: list[str] | None = None) -> list[str]:
    values = list(source_paths or [])
    if path:
        values.append(path)
    return [str(v).strip() for v in values if str(v).strip()]


def _ok(payload: dict[str, Any]) -> dict[str, Any]:
    payload.setdefault("success", True)
    return payload


def _err(exc: Exception) -> dict[str, Any]:
    return {"success": False, "error": str(exc), "error_type": exc.__class__.__name__}


def _execute(fn, **kwargs: Any) -> dict[str, Any]:
    try:
        result = fn(**kwargs)
        return _ok(result if isinstance(result, dict) else {})
    except Exception as exc:
        return _err(exc)


mcp = FastMCP("ai-pipeline-kit")


@mcp.tool()
def create_run(
    path: str | None = None,
    source_paths: list[str] | None = None,
    run_id: str | None = None,
    runtime_root: str | None = None,
) -> dict[str, Any]:
    paths = _to_source_paths(path=path, source_paths=source_paths)
    if not paths:
        return _err(ValueError("at least one source path is required"))
    if runtime_root:
        set_runtime_root(runtime_root)
    return _execute(ai_pipeline.create_run, run_id=run_id, source_paths=paths)


@mcp.tool()
def add_input(path: str, run_id: str | None = None) -> dict[str, Any]:
    return _execute(ai_pipeline.add_input, path=path, run_id=run_id)


@mcp.tool()
def set_runtime_root_tool(path: str) -> dict[str, Any]:
    try:
        return _ok(set_runtime_root(path))
    except Exception as exc:
        return _err(exc)


@mcp.tool()
def list_inputs(run_id: str | None = None) -> dict[str, Any]:
    resolved = run_id or ai_pipeline.resolve_run_id(None)
    return _ok({"run_id": resolved, "sources": ai_pipeline.list_sources(resolved)})


@mcp.tool()
def list_outputs(run_id: str | None = None) -> dict[str, Any]:
    resolved = run_id or ai_pipeline.resolve_run_id(None)
    return _ok({"run_id": resolved, "outputs": ai_pipeline.list_outputs(resolved)})


@mcp.tool()
def read_output(name: str, run_id: str | None = None, max_chars: int = 20000) -> dict[str, Any]:
    path = ai_pipeline.safe_output_path(name, run_id)
    if not path.exists():
        return _err(FileNotFoundError(f"output not found: {path}"))
    text = path.read_text(encoding="utf-8", errors="replace")
    truncated = len(text) > max_chars
    return _ok(
        {
            "name": path.name,
            "path": str(path),
            "content": text[:max_chars],
            "truncated": truncated,
        }
    )


@mcp.tool()
def write_progress(
    status: str,
    current_step: int = 0,
    run_id: str | None = None,
    failed_step: int | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return _execute(
        ai_pipeline.write_progress,
        status=status,
        current_step=current_step,
        run_id=run_id,
        failed_step=failed_step,
        error=error,
    )


@mcp.tool()
def workflow_status(run_id: str | None = None) -> dict[str, Any]:
    return _ok({"workflow": ai_pipeline.workflow_status(run_id)})


@mcp.tool()
def validate_outputs(run_id: str | None = None) -> dict[str, Any]:
    return _ok({"validation": ai_pipeline.validate_outputs(run_id)})


@mcp.tool()
def status() -> dict[str, Any]:
    return _ok(ai_pipeline.runtime_status())


@mcp.tool()
def reset_run(run_id: str | None = None, fresh: bool = False) -> dict[str, Any]:
    try:
        resolved = ai_pipeline.resolve_run_id(run_id)
        if fresh:
            if resolved:
                sources = ai_pipeline.list_sources(resolved)
                source_paths = [str(item.get("path")) for item in sources if isinstance(item, dict) and item.get("path")]
                return _execute(ai_pipeline.create_run, source_paths=source_paths)
            return _execute(ai_pipeline.create_run)
        if not resolved:
            return _execute(ai_pipeline.create_run)
        out_dir = ai_pipeline.output_dir(resolved)
        shutil.rmtree(out_dir, ignore_errors=True)
        out_dir.mkdir(parents=True, exist_ok=True)
        ai_pipeline.write_progress(status="pending", current_step=0, run_id=resolved)
        return _ok(
            {
                "run_id": resolved,
                "reset": "outputs",
                "run_dir": str(ai_pipeline.run_dir(resolved)),
                "output_dir": str(out_dir),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool()
def template_path() -> dict[str, Any]:
    path = ai_pipeline.PLUGIN_ROOT / "assets" / "templates" / "dashboard-sample.html"
    return _ok({"exists": path.exists(), "path": str(path)})


@mcp.tool()
def help_contract() -> dict[str, Any]:
    return _ok(
        {
            "tools": [
                "create_run",
                "add_input",
                "list_inputs",
                "list_outputs",
                "read_output",
                "write_progress",
                "workflow_status",
                "validate_outputs",
                "status",
                "reset_run",
                "set_runtime_root_tool",
                "template_path",
            ],
        }
    )


@mcp.tool()
def runtime_root() -> dict[str, Any]:
    return _ok({"runtime_root": os.environ.get("AI_PIPELINE_RUNTIME_ROOT")})


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
