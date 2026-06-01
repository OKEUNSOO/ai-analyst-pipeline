---
name: ai-analyst-pipeline
description: Run a durable analyst-ready AI data analysis pipeline for CSV, Excel, JSON, TSV, PDF, or text-table datasets. Use when the user asks to analyze data files, run an AI/data-analysis pipeline, handle multiple datasets, create EDA/KPI/metrics JSON/reproducible Python/notebook/dashboard/report outputs, continue or validate an ai-pipeline run, or inspect run-scoped pipeline outputs.
version: "0.1.0"
platforms: [macos, linux, windows]
user-invocable: true
metadata:
  openclaw:
    tags: [data-analysis, pipeline, reporting]
    category: productivity
---

# AI Pipeline Kit

Execute a run-scoped data analysis workflow. Keep each execution under a durable run folder, read source files from their original paths, and produce analyst-ready artifacts: data contract, dataset profile, analysis plan, EDA, problem definition, KPI summary, metrics JSON, reproducible Python, analyst notebook, deep analysis, dashboard HTML, executive report, and validation report.

## Core Contract

- Resolve the skill root as this folder, the folder containing `SKILL.md`.
- Use `scripts/ai_pipeline.py` for run creation, status, progress, output reads, resets, and validation.
- Do not copy source data into the runtime folder. Record and read the original path from `run.json`.
- Execute dependent stages sequentially. Do not run stages in parallel.
- Before each stage, skip it only when every expected output for that stage already exists in the current run's `outputs/` directory.
- After each stage, verify every expected output file exists before starting the next stage.
- Use source-file evidence only. Do not invent metrics, columns, baselines, dates, or counts.
- For multiple files, create a data contract first: identify grain, keys, concat/join/separate-analysis strategy, and row multiplication risks before combining anything.
- Write all generated artifacts in Korean by default, including Markdown reports and visible dashboard text, unless the user explicitly requests another language. Keep file names, source column names, formulas, code identifiers, and proper nouns unchanged when that preserves accuracy.
- Keep dashboard output self-contained HTML using the bundled template and SVG/Canvas. Do not add CDN chart libraries.

## Runtime Commands

Run helper commands from the skill root, or call the script by absolute path.

```bash
python3 scripts/ai_pipeline.py create-run --path /path/to/data.csv
python3 scripts/ai_pipeline.py status
python3 scripts/ai_pipeline.py workflow-status
python3 scripts/ai_pipeline.py write-progress --status running --current-step 1
python3 scripts/ai_pipeline.py validate-outputs
```

Set `AI_PIPELINE_RUNTIME_ROOT=/path/to/data-ai-pipeline` only when the user requests a non-default runtime. The default runtime is `~/Documents/data-ai-pipeline`.

## Start a Pipeline

1. Require at least one source file path from the user request.
2. Verify each source path exists before creating the run.
3. Create the run:

```bash
python3 scripts/ai_pipeline.py create-run --path <source-file>
```

For multiple source files, repeat `--source-path`:

```bash
python3 scripts/ai_pipeline.py create-run --source-path <file-a> --source-path <file-b>
```

4. Record these fields from the JSON output:
   - `run_id`
   - `run_dir`
   - `output_dir`
   - `source_files[].path`
5. Use those values for every stage in the same run.

If no file path is provided, ask for the path and stop.

## Stage Order

| No | Stage | Reference prompt(s) | Output(s) |
|----|-------|---------------------|-----------|
| 1 | Data contract & profile | `references/agents/data-contract.md`, `references/agents/data-ingestion.md` | `00_data_contract.md`, `01_dataset_profile.md` |
| 2 | Analysis plan & EDA | `references/agents/analysis-plan.md`, `references/agents/eda.md` | `02_analysis_plan.md`, `02_eda_report.md` |
| 3 | Problem definition | `references/agents/problem.md` | `03_problem_definition.md` |
| 4 | KPI summary & metrics JSON | `references/agents/metrics.md` | `04_kpi_summary.md`, `04_metrics.json` |
| 5 | Deep analysis & reproducible notebook | `references/agents/analysis.md`, `references/agents/reproducible-analysis.md` | `05_analysis.py`, `05_analysis.ipynb`, `05_analysis_report.md` |
| 6 | HTML dashboard | `references/agents/dashboard.md` | `06_dashboard.html` |
| 7 | Executive & validation reports | `references/agents/report.md`, `references/agents/validation.md` | `07_executive_report.md`, `08_validation_report.md` |

For each stage:

1. Check whether the output file already exists.
2. If it exists, mark the stage cached and continue.
3. If it does not exist, update progress:

```bash
python3 scripts/ai_pipeline.py write-progress --status running --current-step <N> --run-id <run_id>
```

4. Read only the matching reference prompt(s) for that stage.
5. Produce the artifact(s) at `<output_dir>/<expected-output>`.
6. Verify every file exists and is non-empty.
7. If a stage fails, mark progress failed and stop:

```bash
python3 scripts/ai_pipeline.py write-progress --status failed --current-step <N> --failed-step <N> --error "<reason>" --run-id <run_id>
```

After all expected outputs exist, mark the run complete:

```bash
python3 scripts/ai_pipeline.py write-progress --status complete --current-step 7 --run-id <run_id>
python3 scripts/ai_pipeline.py validate-outputs --run-id <run_id>
```

## Resource Map

- `scripts/ai_pipeline.py`: deterministic run metadata, progress, status, reset, and validation helper.
- `references/agents/*.md`: stage-specific agent instructions. Load only the current stage file.
- `references/rules/analysis-principles.md`: read when analysis quality, KPI definitions, or metric interpretation is uncertain.
- `references/rules/design-system.md`: read when creating or reviewing the dashboard.
- `references/docs/overview.md`: read when explaining the system or checking the full architecture.
- `references/docs/usage.md`: read when giving user-facing usage instructions.
- `assets/templates/dashboard-sample.html`: required base template for `06_dashboard.html`.

## Dashboard Rules

Use `assets/templates/dashboard-sample.html` as the base for dashboard output. Preserve its overall structure, CSS, JavaScript conventions, and class names unless the user explicitly asks for a redesign.

- Use SVG/Canvas charts only. Do not use external chart libraries, external fonts, or CDN assets.
- Write all visible dashboard text in Korean by default.
- Keep KPI numbers black; use color for labels or visual marks only.
- Scale every SVG chart against the actual maximum plotted value.

## Completion Response

On success, report:

- Run ID
- Source file path(s)
- Output directory
- Expected artifact paths, marking cached stages where applicable
- Validation result from `validate-outputs`
- Any skipped, failed, or unverified stages

Do not claim completion until `validate-outputs` reports all expected outputs present.
