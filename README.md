# Chain Project

## Setup & Installation

1. **Clone the repo** and navigate into the project directory.
2. **Install dependencies** (Python 3.12 recommended):
    ```bash
    pip install -r requirements.txt
    ```
3. **Create a `.env` file** in the project root. Example:
    ```env
    FOLDER_ID=your_google_drive_folder_id
    ```
    If `FOLDER_ID` is not set, the app will default to `root`.

## Running the App

```bash
python3.12 src/app.py
```

- The app loads environment variables from `.env` using `python-dotenv`.
- All configuration (like Google Drive folder ID and Google credentials path) should be set in `.env`.
- The agent uses LangChain v0.2+ API patterns and directly instantiates GoogleDriveSearchTool (not via load_tools or string names).

## Synthesis Loop & Commands
- Run the synthesis loop and agent using:
  ```bash
  python3.12 src/app.py
  ```
- All commands and agent logic are Python 3.12 compatible.
- Synthesis, suggestion, and rule/fact-check features are modular and extensible. See `.docs` and `.rules` for details.

## Project Files
- `src/app.py`: Main application logic. Loads env vars from `.env`.
- `requirements.txt`: Python dependencies (alphabetized).
- `.env`: Environment variables (not committed to version control).
- `.rules`: Project rules, method docs, structure, and TODOs.
- `.docs`: Method/class documentation, schemas, and algorithm summaries.
- `.roadmap`: Project status, plan, and PR FAQ.

## Notes
- Always keep documentation and rules up to date with code changes.
- Use Python 3.12 for all development and deployment.

# END README.md
