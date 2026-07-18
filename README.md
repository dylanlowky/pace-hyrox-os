# Pace — HYROX Partner OS v0.4

## Changes

- Fast workout logging
- Tailored Run, Hybrid, Strength and Recovery forms
- Optional average heart rate
- Pain location and notes
- Trained-together flag
- Automatic pace calculation
- Automatic session-RPE training load
- Dynamic weekly dashboard
- Data-driven proactive Coach brief
- Personal milestones and bests
- Distance and training-load progress charts
- No database migration required

## Install

Copy the contents of `pace_ai` over the existing Project 002 PACE folder.

Keep:

- `.env`
- `.venv`

Then restart:

```powershell
Ctrl + C
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```
