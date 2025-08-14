Step 0 — Context Load (no output files)

Prompt to Claude:

You are a senior Python UX engineer. You will build a local GUI on top of an existing CLI app called threadsrecon. The GUI must not refactor core logic; it only orchestrates stages by calling python main.py <stage>.
Accept these constraints: single-file GUI, minimal deps (Streamlit or Gradio), local only, artifacts live under data/.
Confirm you understand goals, non-goals, target users, and constraints. Summarize them in ≤10 bullets. Do not write code.

Step 1 — I/O Contract & Validations (design only)

Prompt to Claude:

Produce a rigorous I/O contract for the GUI. Output a single section with these subsections:

Inputs: usernames (comma-separated), stage (all|scrape|analyze|visualize|report), headless (bool), editable settings.yaml.

Env Vars: THREADSRECON_HEADLESS=1|0.

Paths to validate: /usr/local/bin/chromedriver, /usr/bin/wkhtmltopdf, repo data/ write access, repo settings.yaml.

Side effects: Patch ScraperSettings.usernames list in YAML; never change other keys.

Artifacts to read: data/profiles.json, data/analyzed_profiles.json, data/visualizations/*, data/reports/report.pdf.

Failure states & user messages: invalid YAML, missing binaries, no write perms, subprocess non-zero exit, empty artifacts.

Performance bounds: log stream latency < 1s; UI actions complete without blocking main thread.
Deliver as a crisp, numbered spec. No code.

Step 2 — UX & Interaction Flow (design only)

Prompt to Claude:

Design the GUI flow in detail—still no code. Provide:

Screens: Settings, Run, Artifacts, Logs/status region (global).

Event flow: initial load → validate → edit YAML → set usernames → choose stage & headless → run → live logs → refresh artifacts.

Exact UI copy (labels, tooltips, error texts) for each control and validation.

State model: enumerated states (IDLE, VALIDATING, READY, RUNNING, SUCCESS, FAIL) and transitions.

Telemetry (local-only): what runtime info to show (binary versions, paths, last run time, exit code).
Keep it implementation-neutral but precise.

Step 3 — Deliverables Plan (scaffolding, still no code)

Prompt to Claude:

List the files you will generate and their purpose:

ui_app.py (single-file GUI entrypoint)

README_GUI.md (how to run: venv & Docker)

tests_gui.md (manual QA checklist: 15+ steps)

(optional) scripts/validate_env.sh
For ui_app.py, give function signatures only with 1–2 line docstrings:

load_yaml(path) -> dict

save_yaml(path, data) -> None

patch_usernames(yaml_text, names:list[str]) -> str

validate_paths() -> dict[str,bool]

run_stage_with_logs(stage:str, env:dict) -> Iterator[str]

list_artifacts() -> dict[str, list[str]]

preview_artifact(path:str) -> dict|bytes|None

get_versions() -> dict[str,str]
Specify expected exceptions/error returns, but no code yet.

Step 4 — Implementation (single code file)

Prompt to Claude:

Implement ui_app.py exactly per Steps 1–3 using Streamlit only (no extra libs beyond stdlib+pyyaml if needed). Requirements:

One file, import-minimal.

Layout: left sidebar for Stage, Headless, Usernames; main area tabs: Settings, Run, Artifacts.

Settings tab: loads settings.yaml into a textarea; Save button validates YAML and writes file.

Run tab: button launches python main.py <stage> via subprocess; stream combined stdout/stderr live into a growing text area; show exit code.

Headless checkbox flips THREADSRECON_HEADLESS env var.

Usernames field patches ScraperSettings.usernames in YAML (list of strings).

Artifacts tab: JSON viewers for two JSON files, image gallery for data/visualizations, link/open for data/reports/report.pdf.

On app start, show validation badges for chromedriver, wkhtmltopdf, and data/ write access; disable Run if any are missing.

Handle errors gracefully: invalid YAML, missing files, non-zero exits.

Ensure log streaming latency < 1s (iterate over stdout lines).
Produce the complete, runnable ui_app.py and nothing else in this step.

Step 5 — README (usage & ops)

Prompt to Claude:

Write README_GUI.md. Include:

Prereqs (Python, venv, Streamlit, chromedriver path, wkhtmltopdf path).

Install commands (venv + pip install streamlit pyyaml), and how to run: streamlit run ui_app.py.

Docker-compose snippet to expose port 8501 and mount repo; note shared memory tip.

Troubleshooting: common errors (chromedriver mismatch, invalid YAML, permissions), how to resolve.

Security note: don’t commit settings.yaml or data/.
Keep it concise and copy-executable.

Step 6 — Manual QA

Prompt to Claude:

Create tests_gui.md with a 15–20 step manual test plan covering:

Env validation lights & version readouts

YAML edit (good/bad), save failure handling

Usernames patch correctness (list update only)

Stage runs for scrape and analyze with visible logs

Non-zero exit path (intentional bad stage)

Artifacts previews (JSON, images, PDF) and empty-state messages

Permissions failure simulation (readonly data/)

Performance check: log latency < 1s

Step 7 — Optional Script

Prompt to Claude:

Provide a minimal scripts/validate_env.sh that checks chromedriver, wkhtmltopdf, data write access, and prints a one-line PASS/FAIL summary per check. Keep it POSIX-sh compatible and short.

Step 8 — UX Polish (no refactors)

Prompt to Claude:

List small, zero-refactor UX upgrades as bullet points: tooltips, dark mode toggle, filter text box for logs, “copy path” buttons, persisted last run settings, and an initial “Responsible Use & Limits” modal (text only). No code.

Step 9 — Acceptance Review

Prompt to Claude:

Produce an acceptance checklist mapped to the PRD’s acceptance criteria. Each item must be objectively verifiable (e.g., “With chromedriver missing, Run button is disabled and message X is shown”). Keep to 8–12 items.

Step 10 — Final Turn-in

Prompt to Claude:

Return a final summary with:

File tree of generated files

One-line instructions to launch the GUI

The exact env var to toggle headless

Reminder that data/artifacts live under data/