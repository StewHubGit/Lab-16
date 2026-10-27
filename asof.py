"""Point-in-time training filter. Run: python asof.py"""

# EDITABLE INPUTS: preserve the original row numbers when editing the table.
DECISION_DATE = "2026-03-31"
TABLE = """row,ticker,month_measured,published_on,index
1,AAA,2026-01,2026-02-10,101.0
2,AAA,2026-02,2026-03-10,104.0
3,AAA,2026-03,2026-04-10,109.0
4,AAA,2026-02,2026-03-25,103.0
5,BBB,2026-01,2026-02-10,98.0
6,BBB,2026-02,2026-03-10,97.0
7,BBB,2026-02,2026-03-10,97.0
8,BBB,2026-03,2026-04-10,92.0
9,CCC,2026-01,2026-02-10,110.0
10,CCC,2026-02,2026-04-05,112.0
11,,2026-02,2026-03-10,99.0
12,CCC,2026-02,2026-03-10,111.0
"""


import csv
from datetime import date
from decimal import Decimal
import io


def read_table(text):
    """Parse inputs once; every row keeps its source row number."""
    rows = []
    seen_numbers = set()
    for cells in csv.DictReader(io.StringIO(text.strip())):
        number = int(cells["row"])
        if number in seen_numbers:
            raise ValueError(f"Repeated source row number: {number}")
        seen_numbers.add(number)
        rows.append({
            "row": number,
            "ticker": cells["ticker"].strip(),
            "month": date.fromisoformat(cells["month_measured"].strip() + "-01"),
            "published": date.fromisoformat(cells["published_on"].strip()),
            "index": Decimal(cells["index"].strip()),
        })
    return rows


def remove_duplicates(rows):
    """Keep the first exact data duplicate; row number is provenance, not data."""
    kept, removed, seen = [], [], set()
    for row in rows:
        key = (row["ticker"], row["month"], row["published"], row["index"])
        if key in seen:
            removed.append(row)
        else:
            seen.add(key)
            kept.append(row)
    return kept, removed


def latest_publications(rows):
    """Keep the latest publication for each ticker and measured month."""
    latest = {}
    for row in rows:
        key = (row["ticker"], row["month"])
        if key not in latest or row["published"] > latest[key]["published"]:
            latest[key] = row
        elif (row["published"] == latest[key]["published"]
              and row["index"] != latest[key]["index"]):
            raise ValueError(f"Conflicting same-day publications: rows "
                             f"{latest[key]['row']} and {row['row']}")
    kept = [row for row in rows if latest[(row["ticker"], row["month"])] is row]
    removed = [row for row in rows if latest[(row["ticker"], row["month"])] is not row]
    return kept, removed


def report_rule(number, description, removed, remaining):
    numbers = ", ".join(str(row["row"]) for row in removed) or "none"
    print(f"  {number}. {description}: removed {len(removed)} "
          f"(rows: {numbers}); {len(remaining)} remain")


def signal(panel, ticker):
    """Return the latest month and its percent change from the previous month."""
    rows = sorted((row for row in panel if row["ticker"] == ticker),
                  key=lambda row: row["month"])
    if not rows:
        return "N/A (no eligible months)"
    latest = rows[-1]
    month = latest["month"].strftime("%Y-%m")
    if len(rows) < 2:
        return f"{month}: N/A (previous month unavailable)"
    previous = rows[-2]
    month_gap = ((latest["month"].year - previous["month"].year) * 12
                 + latest["month"].month - previous["month"].month)
    if month_gap != 1:
        return f"{month}: N/A (previous month unavailable)"
    if previous["index"] == 0:
        return f"{month}: N/A (previous index is zero)"
    change = (latest["index"] / previous["index"] - 1) * 100
    return (f"{month}: {change:+.2f}% "
            f"({latest['index']} / {previous['index']} - 1; "
            f"rows {previous['row']} -> {latest['row']})")


def main():
    rows = read_table(TABLE)
    decision = date.fromisoformat(DECISION_DATE)
    print(f"DECISION DATE: {decision} (publications on this day are eligible)")
    print(f"\nROW FUNNEL: {len(rows)} input rows")

    panel = [row for row in rows if row["ticker"]]
    removed = [row for row in rows if not row["ticker"]]
    report_rule(1, "Quarantine missing ticker", removed, panel)

    panel, removed = remove_duplicates(panel)
    report_rule(2, "Remove exact duplicates", removed, panel)
    # Same valid, deduplicated input for both calculations. Only as-of uses cutoff.
    naive_input = list(panel)

    removed = [row for row in panel if row["published"] > decision]
    panel = [row for row in panel if row["published"] <= decision]
    report_rule(3, "Remove late publications", removed, panel)

    panel, removed = latest_publications(panel)
    report_rule(4, "Keep latest knowable revision", removed, panel)

    print("\nAS-OF PANEL")
    print(f"{'Row':>3}  {'Ticker':<6}  {'Month measured':<14}  {'Published on':<12}  {'Index':>8}")
    for row in sorted(panel, key=lambda row: (row["ticker"], row["month"])):
        print(f"{row['row']:>3}  {row['ticker']:<6}  {row['month']:%Y-%m}         "
              f"{row['published']}    {row['index']:>8}")
    if not panel:
        print("(empty)")

    naive_panel, _ = latest_publications(naive_input)
    print("\nSIGNALS: latest month / previous month - 1, expressed as a percent")
    print("Naive uses the latest publication for every measured month, ignoring the cutoff.")
    for ticker in sorted({row["ticker"] for row in rows if row["ticker"]}):
        print(f"  {ticker} as-of  {signal(panel, ticker)}")
        print(f"  {ticker} naive  {signal(naive_panel, ticker)}")


if __name__ == "__main__":
    main()
