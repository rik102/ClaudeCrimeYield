import argparse
import csv
import json
import os
from collections import defaultdict
from typing import Dict

NULL_LIKE = {"", "null", "none", "nan", "n/a", "na", "unknown"}
NEGATIVE = {"no", "n", "false", "0", "none", "not found", "no contraband"}
SUCCESS_KEYWORDS = ("arrest", "citation", "cited", "booked")


def norm(value: str) -> str:
    if value is None:
        return ""
    return value.strip()


def norm_lower(value: str) -> str:
    return norm(value).lower()


def is_present(value: str) -> bool:
    v = norm_lower(value)
    return v not in NULL_LIKE


def is_positive(value: str) -> bool:
    v = norm_lower(value)
    return v not in NULL_LIKE and v not in NEGATIVE


def pick_label(*values: str, fallback: str = "Unknown") -> str:
    for value in values:
        v = norm(value)
        if is_present(v):
            return v
    return fallback


def split_reasons(value: str) -> list[str]:
    raw = norm(value)
    if not raw:
        return []
    parts = [p.strip() for p in raw.split("|")]
    return [p for p in parts if p]


def is_unknown_label(value: str) -> bool:
    v = norm_lower(value)
    return (v in NULL_LIKE) or ("unknown" in v)


def is_unknown_beat(beat_code: str, beat_label: str) -> bool:
    code = norm(beat_code)
    if code.startswith("999"):
        return True
    return is_unknown_label(beat_label)


def write_grouped_table(path: str, grouped: Dict[str, Dict[str, int]], key_name: str) -> None:
    rows = []
    for key, stats in grouped.items():
        stops = stats.get("stops", 0)
        success = stats.get("success", 0)
        contraband = stats.get("contraband", 0)
        searches = stats.get("searches", 0)

        row = {
            key_name: key,
            "stops": stops,
            "success": success,
            "yield": round((success / stops) if stops else 0.0, 4),
            "contraband_discoveries": contraband,
        }

        if searches:
            row["searches"] = searches
            row["search_yield"] = round((contraband / searches), 4)

        rows.append(row)

    rows.sort(key=lambda r: (r.get("stops", 0), r.get("yield", 0)), reverse=True)

    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: str, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def read_csv_rows(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute RIPA yield tables from merged CSV.")
    parser.add_argument("--input", default="RIPA_Joined_Data.csv", help="Input merged CSV path")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    by_beat = defaultdict(lambda: {"stops": 0, "success": 0, "contraband": 0})
    by_stop_reason = defaultdict(lambda: {"stops": 0, "success": 0, "contraband": 0})
    by_search_reason = defaultdict(lambda: {"searches": 0, "contraband": 0})

    total_stops = 0
    total_success = 0
    total_contraband = 0
    excluded_unknown_beats = 0

    with open(args.input, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            beat = pick_label(row.get("BEATNAME"), row.get("BEAT"))
            beat_code = norm(row.get("BEAT"))
            if is_unknown_beat(beat_code, beat):
                excluded_unknown_beats += 1
                continue

            total_stops += 1
            stop_reason = pick_label(
                row.get("REASONFORSTOPCODETEXT"),
                row.get("REASONFORSTOPDETAIL"),
                row.get("REASONFORSTOP"),
            )
            search_reason_raw = pick_label(
                row.get("BASISFORSEARCH"),
                row.get("BASISFORSEARCHEXPLANATION"),
                fallback="",
            )

            result_text = norm_lower(row.get("RESULTTEXT"))
            contraband_found = is_positive(row.get("CONTRABAND"))
            property_seized = is_present(row.get("TYPEOFPROPERTYSEIZED")) or is_present(row.get("BASISFORPROPERTYSEIZURE"))
            enforcement_outcome = any(keyword in result_text for keyword in SUCCESS_KEYWORDS)
            success = enforcement_outcome or contraband_found or property_seized

            by_beat[beat]["stops"] += 1
            if not is_unknown_label(stop_reason):
                by_stop_reason[stop_reason]["stops"] += 1

            if success:
                total_success += 1
                by_beat[beat]["success"] += 1
                if not is_unknown_label(stop_reason):
                    by_stop_reason[stop_reason]["success"] += 1

            if contraband_found:
                total_contraband += 1
                by_beat[beat]["contraband"] += 1
                if not is_unknown_label(stop_reason):
                    by_stop_reason[stop_reason]["contraband"] += 1

            search_reasons = split_reasons(search_reason_raw)
            for search_reason in search_reasons:
                if is_unknown_label(search_reason):
                    continue
                by_search_reason[search_reason]["searches"] += 1
                if contraband_found:
                    by_search_reason[search_reason]["contraband"] += 1

    # Convert search table into the same writing shape.
    search_table = {}
    for reason, stats in by_search_reason.items():
        searches = stats["searches"]
        contraband = stats["contraband"]
        search_table[reason] = {
            "stops": searches,
            "success": contraband,
            "contraband": contraband,
            "searches": searches,
        }

    write_grouped_table(os.path.join(args.output_dir, "yield_by_beat.csv"), by_beat, "beat")
    write_grouped_table(os.path.join(args.output_dir, "yield_by_stop_reason.csv"), by_stop_reason, "stop_reason")
    write_grouped_table(os.path.join(args.output_dir, "search_yield_by_reason.csv"), search_table, "search_reason")
    write_json(
        os.path.join(args.output_dir, "yield_by_beat.json"),
        read_csv_rows(os.path.join(args.output_dir, "yield_by_beat.csv")),
    )
    write_json(
        os.path.join(args.output_dir, "yield_by_stop_reason.json"),
        read_csv_rows(os.path.join(args.output_dir, "yield_by_stop_reason.csv")),
    )
    write_json(
        os.path.join(args.output_dir, "search_yield_by_reason.json"),
        read_csv_rows(os.path.join(args.output_dir, "search_yield_by_reason.csv")),
    )

    overall = {
        "total_stops": total_stops,
        "stops_with_enforcement_outcome": total_success,
        "contraband_discoveries": total_contraband,
        "overall_yield": round((total_success / total_stops) if total_stops else 0.0, 4),
        "excluded_unknown_beats": excluded_unknown_beats,
    }

    overall_path = os.path.join(args.output_dir, "overall_summary.csv")
    with open(overall_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(overall.keys()))
        writer.writeheader()
        writer.writerow(overall)
    write_json(os.path.join(args.output_dir, "overall_summary.json"), [overall])

    print("Wrote:")
    print(f"- {os.path.join(args.output_dir, 'yield_by_beat.csv')}")
    print(f"- {os.path.join(args.output_dir, 'yield_by_stop_reason.csv')}")
    print(f"- {os.path.join(args.output_dir, 'search_yield_by_reason.csv')}")
    print(f"- {overall_path}")
    print("\\nOverall:")
    for k, v in overall.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
