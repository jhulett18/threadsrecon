PRODUCT REQUIREMENTS DOCUMENT (PRD) — threadsrecon GUI Orchestration Tool
1. Overview
We are adding a local GUI layer on top of the existing threadsrecon CLI tool to allow non-technical
users to:
- Edit configuration (settings.yaml)
- Select targets/usernames
- Choose which pipeline stage to run (all, scrape, analyze, visualize, report)
- Toggle headless browsing
- See live logs while a stage runs
- Preview generated artifacts (JSON, images, PDF)
Key requirement: No refactoring of threadsrecon’s core logic. GUI will orchestrate by calling main.py
with the proper arguments.
2. Goals & Non-Goals
Goals:
- Simplify execution for non-technical users
- Preserve all CLI functionality
- Provide live visibility into scraping/analysis progress
- Enable quick artifact review inside the GUI
Non-Goals:
- Changing or optimizing the scraping logic
- Hosting a multi-user web application
- Adding new analysis features beyond what threadsrecon already does
3. Target Users
- Researchers
- OSINT analysts
- Social media monitoring teams
- Non-developers who want to run Threads data analysis without CLI
4. Functional Requirements
4.1 Settings Management:
- Load settings.yaml from repo root
- Display YAML in editable text area
- Save back to file with validation (must remain valid YAML)
- Patch behavior: When usernames are entered in GUI, update ScraperSettings.usernames in the
YAML
4.2 Run Pipeline:
- Inputs:
- Usernames: comma-separated
- Stage selector: one of {all, scrape, analyze, visualize, report}
- Headless toggle: boolean → maps to env var THREADSRECON_HEADLESS
- On “Run” click:
- Validate prerequisites (chromedriver, wkhtmltopdf paths, write access to data/)
- Launch python main.py as subprocess
- Stream combined stdout/stderr into a scrolling log panel
4.3 Artifact Preview:
- JSON files: Render profiles.json and analyzed_profiles.json as collapsible JSON viewers
- Images: Display thumbnails from data/visualizations/
- PDF: Link or embed data/reports/report.pdf
- Auto-refresh preview after run completes
4.4 Environment Validation:
- On GUI launch, verify:
- chromedriver exists at /usr/local/bin/chromedriver
- wkhtmltopdf exists at /usr/bin/wkhtmltopdf
- data/ directory is writable
- Show status indicators (green check or red X) for each
5. Non-Functional Requirements
- Local-only: Runs on user’s machine, no network API except Threads scraping
- Dependencies: Only allow streamlit or gradio + Python stdlib (no heavy frameworks)
- Performance: Log streaming should update in near real-time (< 1s delay)
- Portability: Must work in both venv and Docker-compose setups
6. Error Handling
- Invalid YAML → block Save/Run, show parse error
- Missing prerequisites → disable Run, show fix instructions
- Subprocess non-zero exit → highlight in logs, show final status as “Failed”
- Empty/missing artifacts → show “No data yet” message
7. Deliverables for Claude
- ui_app.py (single-file GUI entrypoint)
- README_GUI.md (usage instructions for local + Docker)
- tests_gui.md (manual QA checklist)
- Optional: scripts/validate_env.sh for environment checks
8. User Flow
1. User launches GUI (streamlit run ui_app.py or Docker port 8501)
2. Environment check runs; status shown
3. User edits settings.yaml or just enters usernames
4. User selects stage + headless toggle
5. User clicks “Run” → logs stream in real-time
6. On completion, GUI refreshes artifact previews
7. User can click “View” to open PDFs/images or expand JSON
9. Constraints
- Must preserve relative paths (settings.yaml, data/) in repo root
- No new folders outside repo root
- Must not alter CLI argument format of main.py
10. Acceptance Criteria
- Editing and saving settings.yaml works with validation
- Usernames entered in GUI update YAML correctly
- Environment checks block execution if prerequisites missing
- Pipeline stages execute with visible logs
- Generated artifacts preview correctly
- Works in both venv and Docker-compose environments