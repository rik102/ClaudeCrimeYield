python analyze_ripa.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python build_insight_report.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python server.py
