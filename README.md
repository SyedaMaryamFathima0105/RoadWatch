# RoadWatch

RoadWatch is a student road-damage reporting prototype. Users can upload a road photo, add an optional location and note, view accepted reports on a map, and review reports through the local admin dashboard.

## Run the website

1. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/windows/). During installation, enable **Add python.exe to PATH**.
2. Close and reopen VS Code.
3. Open the RoadWatch folder in VS Code.
4. Open the terminal and run:

```powershell
.\run-roadwatch.bat
```

5. Open http://127.0.0.1:8000 in your browser.

## Requirements

- Python 3.11 or newer
- Internet connection for OpenStreetMap map tiles

No Java, Node.js, Docker, database server, or additional Python libraries are required.

To verify Python before starting, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\check-setup.ps1
```

The default admin API key is:

```text
change-this-admin-key
```

This is an academic prototype. AI results, when an AI model is connected, are suggestions that require human review.
