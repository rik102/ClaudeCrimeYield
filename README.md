# Impact Yield Analyzer (San Diego RIPA)

## Team Name
Impact Yield Analyzer

## Team Members
- Riksean Rosholt - Data engineering, analysis pipeline, frontend dashboard
- Shikha Gupta
- Gaurav Bansal
- Jerry Hall, Civic advocate, criminal-legal and behavioral health systems advocacy  

## Problem Statement
By better understanding police activities, California law enforcement are required to collect and publish officer reports of every stop, pedestrian, traffic, or other means.  

Now, residents can view, browse, query, and even use a chat function to query this data. Now, we can understand not only officer activities, we can learn more about issues and gaps our neighborhoods are experiencing, ideally to focus solutions to help eliminate the need for future law enforcement. 

The tool also illustrates through a map, visualizations, and data a variety of stop-related data including race, reason for the stop, searches, contraband, and if the individual was warned, cited, or arrested.  

This project quantifies **stop yield** across San Diego geographies and stop contexts to identify where stop activity is high but outcomes are low.

This project was a submission at the Anthropic 'Claude Impact Lab` (`https://luma.com/6ok9h92y`) event hosted by Max Krueger from `Backland Labs` (`https://github.com/Backland-Labs/city-of-sd-hackathon`)

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

5. **Claude integration approach**
- **How Claude was used to build it:** Claude was used during development to iterate on metric logic, improve data-processing scripts, and speed up dashboard/map implementation and deployment fixes.
- **How Claude is used inside the app:** The deployed MVP is a static data dashboard and does not make live Claude API calls at runtime. Claude-assisted narrative summaries are produced from computed tables and saved to `output/insight_report.md`.

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
- 60-second walkthrough: https://github.com/bansal1600/ripa-data

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
