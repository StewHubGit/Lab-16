# Lab 16 data card

| Field | Record |
| --- | --- |
| Source | The complete 12-row training table pasted by the user during the Lab 16 session on 2026-10-27. The user subsequently supplied the expected row funnel, panel and six signals. |
| Measure | Monthly index levels for the teaching tickers AAA, BBB and CCC. No actual market securities or economic series identifiers were supplied. |
| Units | Index points. The base date and base level were not specified. Values are not assumed to be prices per 100 of bond face value. Signals are unannualized month-to-month percent changes. |
| Measured periods | January, February and March 2026, depending on ticker. |
| Decision date | 2026-03-31, inclusive; all publications dated on or before that day are eligible. |
| Initial publication lag in supplied table | January values: February 10, 10 calendar days after January 31. First February values: March 10, 10 days after February 28. March values: April 10, 10 days after March 31. |
| Revisions | AAA February: row 2, 104.0 published March 10, replaced by row 4, 103.0 published March 25 (25 days after February month-end). CCC February: row 12, 111.0 published March 10, later revised to row 10, 112.0 published April 5 (36 days after February month-end). |
| Duplicate | BBB row 7 duplicates row 6: same ticker, measured month, publication date and index. Retain row 6. |
| Quarantine | Row 11 has no ticker and is quarantined before duplicate handling. |
| Download/acquisition date | No external data download. The user-supplied table was transcribed into the script on 2026-10-27. |
| Row provenance | Original user-supplied row numbers 1 through 12 are preserved, including for removed rows. |
| Availability basis | Publication dates are supplied as part of the training case; they were not independently matched to actual financial-market releases. |
| Transformations | Parse dates and numeric levels, apply four rules in order, calculate consecutive-month percentage changes with Decimal arithmetic, display two decimals. No interpolations, estimated lags or annualization. |
| Real-series requirement | Establish actual publication history and revisions. If a publication date cannot be found, quarantine the affected series until it can be established. |

## ALFRED context

[ALFRED](https://alfred.stlouisfed.org/help) archives historical versions of economic data, making it possible to examine values as they were reported in the past. Its [download help](https://alfred.stlouisfed.org/help/downloaddata) distinguishes an observation date from the real-time interval over which a version was current. The observation date cannot serve as evidence that the value was public on that date.

The FRED category URL discussed during the session is a documentation example for category 125, Trade Balance. Its key `abcdefghijklmnopqrstuvwxyz123456` is a demonstration placeholder. [Category documentation](https://fred.stlouisfed.org/docs/api/fred/category.html). It does not provide the training table's publication history.

For a real-series check, [the observations API](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) can request a historical information set with `realtime_start` and `realtime_end` both set to the decision date. A full removal audit needs vintage history as well. Document whether availability means source release, ALFRED vintage validity, or receipt by a particular investor: [release dates and website availability can differ](https://fred.stlouisfed.org/docs/api/fred/releases_dates.html). The submitted script makes no API requests and requires no API key.
