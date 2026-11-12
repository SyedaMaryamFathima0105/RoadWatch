# RoadWatch

RoadWatch is a student-built web application for reporting visible road damage. A user can upload a road photo, optionally add a location and note, and submit the report for review. Administrators can review reports, update their status, view nearby report groups, and see accepted reports on an interactive map.

## Key features

- Upload road-damage photos with an optional location and note
- Group reports submitted within 30 metres of the same location
- Review, accept, reject, or mark reports as repaired
- View accepted reports on an OpenStreetMap map
- Store report history and status changes in a local audit trail

## Run locally

1. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/windows/). In the installer, enable **Add python.exe to PATH**.
2. Close and reopen VS Code after installation.
3. Open the RoadWatch project folder.
4. Run the following command in the VS Code terminal:

```powershell
.\run-roadwatch.bat
```

5. Open http://127.0.0.1:8000 in your browser.

## Requirements

- Python 3.11 or newer
- Internet connection for OpenStreetMap map tiles

RoadWatch uses Python's built-in SQLite database, so no Docker, Java, Node.js, database server, or extra Python packages are required.

To confirm that Python is ready, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\check-setup.ps1
```

## Project structure

| Path | Purpose |
| --- | --- |
| `app.py` | Python server, API routes, validation, SQLite storage, grouping, and audit trail |
| `python-web/` | Website pages, styling, and browser behaviour |
| `run-roadwatch.bat` | Windows launcher |
| `uploads/` | Locally saved report images, created when the app runs |

## Admin access

Open the **Admin** page and enter the local development key:

```text
change-this-admin-key
```

## Prototype notice

RoadWatch is an academic prototype. It does not replace professional road inspection, emergency services, or official civic complaint systems. Any AI result is a suggestion that requires human review.
