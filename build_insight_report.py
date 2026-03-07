import csv
from pathlib import Path

OUT = Path("output")


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_num(v, t=float):
    try:
        return t(v)
    except Exception:
        return t(0)


def fmt_pct(v):
    return f"{(float(v) * 100):.1f}%"


def main():
    summary = read_csv(OUT / "overall_summary.csv")[0]
    beats = [r for r in read_csv(OUT / "yield_by_beat.csv") if to_num(r["stops"], int) >= 1000]
    reasons = [r for r in read_csv(OUT / "yield_by_stop_reason.csv") if to_num(r["stops"], int) >= 500]
    search = [r for r in read_csv(OUT / "search_yield_by_reason.csv") if to_num(r["searches"], int) >= 200]

    low_beats = sorted(beats, key=lambda r: to_num(r["yield"]))[:5]
    high_beats = sorted(beats, key=lambda r: to_num(r["yield"]), reverse=True)[:5]
    low_reasons = sorted(reasons, key=lambda r: to_num(r["yield"]))[:5]
    high_search = sorted(search, key=lambda r: to_num(r["search_yield"]), reverse=True)[:5]

    lines = []
    lines.append("# RIPA Yield Insight Report")
    lines.append("")
    lines.append("## Overall")
    lines.append(f"- Total stops: {int(summary['total_stops']):,}")
    lines.append(f"- Stops with enforcement outcome: {int(summary['stops_with_enforcement_outcome']):,}")
    lines.append(f"- Contraband discoveries: {int(summary['contraband_discoveries']):,}")
    lines.append(f"- Overall yield: {fmt_pct(summary['overall_yield'])}")
    lines.append("")

    lines.append("## High Activity, Lowest Yield Beats (>= 1,000 stops)")
    for r in low_beats:
        lines.append(f"- {r['beat']}: {int(r['stops']):,} stops, {fmt_pct(r['yield'])} yield")
    lines.append("")

    lines.append("## High Activity, Highest Yield Beats (>= 1,000 stops)")
    for r in high_beats:
        lines.append(f"- {r['beat']}: {int(r['stops']):,} stops, {fmt_pct(r['yield'])} yield")
    lines.append("")

    lines.append("## Lowest Yield Stop Reasons (>= 500 stops)")
    for r in low_reasons:
        lines.append(f"- {r['stop_reason']}: {int(r['stops']):,} stops, {fmt_pct(r['yield'])} yield")
    lines.append("")

    lines.append("## Highest Search Yield Reasons (>= 200 searches)")
    for r in high_search:
        lines.append(
            f"- {r['search_reason']}: {int(r['searches']):,} searches, {int(r['contraband_discoveries']):,} contraband, {fmt_pct(r['search_yield'])} search yield"
        )
    lines.append("")

    lines.append("## Interpretation")
    lines.append("- Focus review where stop activity is high and enforcement yield is low.")
    lines.append("- Compare low-yield stop reasons against policy goals and deployment patterns.")
    lines.append("- Use search-yield differences to evaluate search basis effectiveness.")

    out_path = OUT / "insight_report.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
