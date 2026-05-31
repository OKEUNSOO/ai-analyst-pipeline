from __future__ import annotations

from plugins.ai_analyst_pipeline.cli import register_cli, ai_pipeline_command
from plugins.ai_analyst_pipeline.tools import (
    AI_PIPELINE_CREATE_RUN_SCHEMA, handle_create_run,
    AI_PIPELINE_STATUS_SCHEMA, handle_status,
    AI_PIPELINE_WORKFLOW_STATUS_SCHEMA, handle_workflow_status,
    AI_PIPELINE_LIST_INPUTS_SCHEMA, handle_list_inputs,
    AI_PIPELINE_LIST_OUTPUTS_SCHEMA, handle_list_outputs,
    AI_PIPELINE_READ_OUTPUT_SCHEMA, handle_read_output,
    AI_PIPELINE_WRITE_PROGRESS_SCHEMA, handle_write_progress,
)

_TOOLS = [
    ("ai_pipeline_create_run",      AI_PIPELINE_CREATE_RUN_SCHEMA,      handle_create_run,      "📊"),
    ("ai_pipeline_status",          AI_PIPELINE_STATUS_SCHEMA,          handle_status,          "ℹ️"),
    ("ai_pipeline_workflow_status", AI_PIPELINE_WORKFLOW_STATUS_SCHEMA, handle_workflow_status, "📋"),
    ("ai_pipeline_list_inputs",     AI_PIPELINE_LIST_INPUTS_SCHEMA,     handle_list_inputs,     "📂"),
    ("ai_pipeline_list_outputs",    AI_PIPELINE_LIST_OUTPUTS_SCHEMA,    handle_list_outputs,    "📁"),
    ("ai_pipeline_read_output",     AI_PIPELINE_READ_OUTPUT_SCHEMA,     handle_read_output,     "📄"),
    ("ai_pipeline_write_progress",  AI_PIPELINE_WRITE_PROGRESS_SCHEMA,  handle_write_progress,  "✍️"),
]


def register(ctx) -> None:
    for name, schema, handler, emoji in _TOOLS:
        ctx.register_tool(
            name=name,
            toolset="ai_analyst_pipeline",
            schema=schema,
            handler=handler,
            emoji=emoji,
        )

    ctx.register_cli_command(
        name="ai-pipeline",
        help="AI data analysis pipeline (run, status, workflow, inputs, outputs, read)",
        setup_fn=register_cli,
        handler_fn=ai_pipeline_command,
        description="7-stage AI data analysis pipeline — create runs, track progress, read outputs.",
    )
