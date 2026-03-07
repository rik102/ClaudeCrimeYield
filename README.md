# Impact Yield Analyzer (San Diego RIPA)

## Team Name
Impact Yield Analyzer

## Team Members
- Rikro - Data engineering, analysis pipeline, frontend dashboard
- Codex assistant - API scaffolding, visualization UI, reporting automation

## Problem Statement
Cities can measure how much policing occurs, but they often do not measure whether those actions produce meaningful enforcement outcomes.

This project quantifies **stop yield** across San Diego geographies and stop contexts to identify where stop activity is high but outcomes are low.

## What It Does
The app ingests a merged RIPA dataset and computes:
- Total stops
- Stops with enforcement outcomes
- Contraband discoveries
- Yield by beat
- Yield by stop reason
- Search yield by search basis

It then serves an interactive dashboard with filters for minimum volume thresholds so users can focus on high-confidence patterns (not tiny samples).

## Data Sources Used
- City of San Diego / California RIPA stop data (merged file: `RIPA_Joined_Data.csv`)
- Derived output tables in `/output`:
  - `yield_by_beat.csv/json`
  - `yield_by_stop_reason.csv/json`
  - `search_yield_by_reason.csv/json`
  - `overall_summary.csv/json`

## Architecture / Approach
1. **Analysis pipeline** (`analyze_ripa.py`)
- Reads merged CSV in a streaming manner (no pandas dependency)
- Defines success as: arrest/citation OR contraband found OR property seizure indicators
- Writes summary tables to `/output` in CSV and JSON

2. **Insight report generator** (`build_insight_report.py`)
- Produces `output/insight_report.md` with headline findings and narrative bullets

3. **Local API + app server** (`server.py`)
- Serves static files and JSON API endpoints:
  - `/api/summary`
  - `/api/yield/beat`
  - `/api/yield/reason`
  - `/api/yield/search`

4. **Frontend dashboard** (`index.html`)
- KPI cards + filtered low/high yield rankings
- Search-yield table
- Narrative insight panel for presentation/demo

## How To Run
1. Generate analysis outputs:

```powershell
python analyze_ripa.py
python build_insight_report.py
```

2. Start local app:

```powershell
python server.py
```

3. Open in browser:
- `http://127.0.0.1:8000`

Or run everything in one step:

```powershell
.\run_demo.ps1
```

## Links
- Live application: Local demo via `python server.py` (`http://127.0.0.1:8000`)
- Repository: This project directory

## Demo Video
- 60-second walkthrough: pending

## Current MVP Result Snapshot
From current merged dataset run:
- Total stops: 213,131
- Enforcement outcomes: 12,894
- Contraband discoveries: 11,618
- Overall yield: 6.05%

See full narrative output at `output/insight_report.md`.

## Next Extension (Post-MVP)
- Add CFS and NIBRS joins to show: **activity vs. outcomes vs. crime**
- Add beat geometry layer for full choropleth map view
- Add time-series trend line by quarter/month
