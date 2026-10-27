# Lab 16 - Point-in-time data and look-ahead bias

Prepared for GitHub submission on 27 October 2026. Decision date: **31 March 2026**.

The question is: **On the day a decision would have been made, what did the data actually say, and how much of the apparent signal arrived later?** The submitted script reproduces the supplied training answer for AAA, BBB and CCC using the original 12 row numbers.

## Files and run command

| File | Purpose |
| --- | --- |
| [asof.py](asof.py) | Standalone Python script; editable table and decision date at the top; standard library only. |
| [OUTPUT.txt](OUTPUT.txt) | Unedited standard output captured from running this submitted copy. |
| [DATA_CARD.md](DATA_CARD.md) | Source, measure, units, publication lags, revisions and acquisition date. |
| [VALIDATION.json](VALIDATION.json) | Comparison with the supplied known answer, additional behavioral checks, run details and file hashes. |

Upload this folder's five files together to GitHub. From this folder, run:

```bash
python asof.py
```

On the original Windows workspace, where `python` is not on PATH, run from the main `AIFinance2026` folder:

```powershell
.\.venv\Scripts\python.exe .\Lab16_Point_In_Time\asof.py
```

There are no packages to install, API keys to supply, network requests or input files to download. The table is embedded in `asof.py`. All funnel counts, panels and signals are calculated from the editable inputs; the program contains no typed-in expected answers.

## Representation and the four rules

Each row retains its original row number, ticker, measured month, publication date and index level. The measured month says what period the number describes. The publication date says when that version became knowable. A revision can change a historical period without changing its measured month.

Apply the rules in this order:

1. Quarantine a row with no ticker.
2. Remove an exact duplicate, keeping the first source row. Row number identifies provenance and is excluded from the duplicate comparison.
3. Remove a publication after the decision date. Publications on the decision date are eligible.
4. For each ticker and measured month, retain the latest remaining publication.

Rule 3 must precede rule 4: selecting CCC's later February revision first would erase the February value that was actually available on March 31. The as-of and naive calculations share the same ticker and duplicate handling; naive deliberately skips the publication cutoff.

## Known-answer proof

| Funnel step | Count removed | Original rows removed | Rows remaining |
| --- | ---: | --- | ---: |
| Input | - | - | 12 |
| Missing ticker | 1 | 11 | 11 |
| Exact duplicate | 1 | 7 | 10 |
| Published after March 31 | 3 | 3, 8, 10 | 7 |
| Older eligible vintage | 1 | 2 | 6 |

The surviving panel is:

| Row | Ticker | Month measured | Published on | Index |
| ---: | --- | --- | --- | ---: |
| 1 | AAA | 2026-01 | 2026-02-10 | 101.0 |
| 4 | AAA | 2026-02 | 2026-03-25 | 103.0 |
| 5 | BBB | 2026-01 | 2026-02-10 | 98.0 |
| 6 | BBB | 2026-02 | 2026-03-10 | 97.0 |
| 9 | CCC | 2026-01 | 2026-02-10 | 110.0 |
| 12 | CCC | 2026-02 | 2026-03-10 | 111.0 |

Signal: `(latest month index / previous month index - 1) * 100`. The program requires consecutive months and reports N/A if the previous month is unavailable or its index is zero. It uses `Decimal` arithmetic and formats results to two decimal places. The naive signal uses each measured month's latest publication in the supplied table, ignoring the decision-date cutoff.

| Ticker | As-of signal | Naive signal | Naive minus as-of, percentage points |
| --- | --- | --- | ---: |
| AAA | +1.98% (February) | +5.83% (March) | +3.85 |
| BBB | -1.02% (February) | -5.15% (March) | -4.13 |
| CCC | +0.91% (February) | +1.82% (February, revised) | +0.91 |

Differences above are calculated before rounding. [OUTPUT.txt](OUTPUT.txt) records the actual execution, including the source rows and index ratios behind all six signals. [VALIDATION.json](VALIDATION.json) compares that execution with the supplied answer and records checks with altered inputs and decision dates; expected answers appear only in this report and external validation, not in the submitted program.

## Explanation and reflection

**Look-ahead bias** occurs when a historical decision uses information published after the decision. A naive backtest would claim that AAA's +5.83% March momentum, BBB's -5.15% March decline and CCC's revised +1.82% February change were visible on March 31. The actual signals were +1.98%, -1.02% and +0.91%. These data do not contain later investment outcomes, so this exercise does not establish a strategy's predictive performance.

For **AAA**, rule 3 removes row 3: March's 109.0 arrived on April 10. That later observation creates the +3.85-point gap between the naive and as-of signals. Rule 4 also matters: February's row 4, published March 25, replaces row 2, published March 10. Retaining row 2 would produce `104 / 101 - 1 = +2.97%`, rather than the correct `103 / 101 - 1 = +1.98%`.

For **CCC**, both signals refer to February. The leak comes from the later revision in row 10, published April 5, rather than from switching to a later measured month. Rule 3 excludes it, leaving row 12. This is why a measured-month filter alone is insufficient.

For **BBB**, row 7 is removed because it duplicates row 6. Its index of 97.0 is not, by itself, the reason for removal. The naive March decline looks more severe because row 8 was not published until April 10.

**Index levels and zero-coupon prices:** The training table supplies index levels, without a redemption value or bond maturity. An index normalized to a base such as 100 can exceed 100, so CCC at 111 and BBB at 97 are possible index levels. For an individual zero-coupon bond redeeming at 100, the standard annual-compounding formula is `P = 100 / (1 + y)^T`. With positive time to maturity, a price of 111 implies a negative yield under that formula; 97 is consistent with a positive yield. A zero-coupon bond can still lose market value when yields rise. Thus the table alone does not establish the correct pricing of any particular bond. See [SIX's index glossary](https://www.six-group.com/en/market-data/indices/index-explorer/glossary.html) and the [Federal Reserve's discussion of STRIPS](https://www.federalreserve.gov/boarddocs/supmanual/trading/4000p1.pdf).

## DRIVER - one line each

**Define** - Calculate the consecutive-month signal knowable by the end of March 31, 2026, and compare it with hindsight.

**Represent** - Preserve original row numbers and distinguish measured month, publication date and revision date using the four ordered rules.

**Implement** - Use one standard-library Python file with editable inputs to print the funnel, panel and paired signals.

**Validate** - Match the supplied removal rows, surviving panel and all six signals, then check that changing inputs changes the computed result.

**Evolve** - For a real series, obtain publication and revision history and record its actual availability lag in a data card before reusing the filter.

**Reflect** - A value describing a past period may still be unavailable, and an apparently stronger signal can be information that arrived later.

## Scope and AI assistance

This submission covers the supplied Lab 16 training table. The tickers are teaching labels; no actual FRED/ALFRED series or zero-coupon securities are identified by them. The script uses calendar dates and an end-of-day convention. Intraday trading would require release timestamps and time zones. A real series with unknown publication dates must be quarantined until availability is established, as discussed in the data card.

Codex assisted with the Python implementation, explanation and verification against the user-supplied table and answer key during this session.
