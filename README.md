# ECE-005 – Prepaid IoT SIM Pooled Data Pack Engine — Sample Data Pack
Prepared by 10 SECONDS for Team E025.

Input pack for a pooled prepaid M2M data engine: 3 fleet accounts, 40 SIMs, 2 pack types and 45 days (2026-10-01 … 2026-11-14) of daily usage per SIM, with pack purchases and SIM state changes in commands.txt.

Pack conventions where the brief is silent: validity counts the purchase date as day 1 (a 30-day pack bought on 2026-10-01 is usable through 2026-10-30 and expires at the end of that day). Grace day 1 is the day after expiry. For fair use, the 'purchased pool' is the sum of data_mb of all the account's packs valid on the usage date, and a SIM's counter is its total accepted usage since the purchase date of the oldest currently-valid pack. Daily usage is deducted in date order; within a day, in usage.csv order. Process a day's commands before that day's usage rows.

## Files
| File | What it holds | Rows |
|---|---|---|
| accounts.csv | Fleet customer accounts | 3 |
| sims.csv | SIMs (ICCID) with their account and device type | 40 |
| pack_types.csv | Prepaid pack catalogue | 2 |
| usage.csv | Daily data usage per SIM in MB | 1530 |
| commands.txt | Load commands, dated pack purchases / activations / suspensions, final statements | 63 |

## Column reference
Conventions: dates `YYYY-MM-DD`; timestamps `YYYY-MM-DD HH:MM:SS` (24h, IST, no timezone suffix); money in Rs as plain decimals (no commas, no symbol); percentages as plain numbers (12.5 = 12.5%); booleans `true`/`false`; IDs uppercase with a fixed prefix.

### accounts.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| account_id | string | ACC-nn | ACC-01 … ACC-03 | Primary key |
| account_name | string | - |  |  |
| city | string | - |  |  |
| contact_mobile | string | 10 digits | starts 6–9 |  |

### sims.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| iccid | string | 19 digits starting 8991 | unique | Primary key |
| account_id | string | ACC-nn | must exist |  |
| device_type | string | - | GPS_TRACKER, POS, SMART_METER, SENSOR_NODE | Not used by any rule |
| registered_date | date | YYYY-MM-DD | Sep 2026 | Registration only; ACTIVATE commands switch SIMs on |

### pack_types.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| pack_type | string | PK-x | PK-S, PK-L | Primary key |
| data_mb | integer | MB |  | Added to the account pool |
| validity_days | integer | days | 30 | Purchase date counts as day 1 |
| price_rs | decimal | Rs |  | Before GST |
| overage_rate_per_mb | decimal | Rs per MB |  | Applied per whole MB (rounded up) per SIM per day |

### usage.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| date | date | YYYY-MM-DD | 2026-10-01 … 2026-11-14 | Sorted by date then ICCID (planted traps at the end) |
| iccid | string | 19 digits | should exist in sims.csv (one planted unknown) |  |
| mb_used | decimal | MB, 1 decimal | > 0 |  |

## Command file format
`commands.txt` holds one command per line as `COMMAND_NAME|arg1|arg2|...`. Commands must be processed in file order, top to bottom. Lines starting with `#` are comments and blank lines are ignored.

| Command | Arguments (in order) | Meaning |
|---|---|---|
| LOAD_ACCOUNTS / LOAD_SIMS / LOAD_PACK_TYPES / LOAD_USAGE | file | Load the named CSV |
| BUY_PACK | account_id \| pack_type \| date | Add a pack to the account pool from that date |
| ACTIVATE | iccid \| date | SIM becomes ACTIVE from that date |
| SUSPEND | iccid \| date | ACTIVE → SUSPENDED |
| RESUME | iccid \| date | SUSPENDED → ACTIVE |
| REGISTER_SIM | iccid \| account_id \| device_type \| date | Re-register a DEACTIVATED SIM (state becomes registered/inactive until ACTIVATE) |
| STATEMENT | account_id \| period_start \| period_end | Print the account statement for the period |

`account_state` in pool_log.csv is ACTIVE, EXPIRED or DEACTIVATED (the state of the account's SIMs on that day). `final_state` is ACTIVE, SUSPENDED, EXPIRED or DEACTIVATED. `total_rs` is rounded to the nearest rupee (format 1234.00).

## Planted scenarios
Line numbers count the header row as line 1, so the first data row of a CSV is line 2. For commands.txt the line number is the physical line in the file (comment lines included).

- **Usage on the pack's last validity day** — ACC-01's PK-S bought 2026-10-01 (commands.txt line 6) is valid through 2026-10-30 (day 30). usage.csv line 999 (8991860001815188447, 41.2 MB on 2026-10-30) is still served from the pool; line 1035 (2026-10-31) must be rejected as EXPIRED.
- **Two packs overlapping (older pack must drain first)** — ACC-02 holds PK-L bought 2026-10-01 (line 7, valid to 2026-10-30) and PK-L bought 2026-10-20 (line 51, valid to 2026-11-18). From 2026-10-20 both are valid: the October-1 pack must drain first; whatever is left of it lapses at the end of 2026-10-30.
- **SIM using exactly 20% of the pool** — 8991860028158464506 (ACC-03) uses exactly 4096.0 MB = 20% of the 20480 MB pool over 2026-10-01 … 2026-10-25 (last row usage.csv line 856): no overage yet. Its next row on 2026-10-26 (line 888, 123.4 MB) is entirely beyond fair use → 124 MB overage even though the pool still has data.
- **Account with one SIM only (fair-use rule becomes 20% so overage from day one is likely)** — ACC-01 has a single SIM (8991860001815188447) on a 1024 MB pack: its fair-use cap is 204.8 MB, so overage starts from about the 6th day of usage (rows begin at usage.csv line 2) while 800+ MB of pool remains unused.
- **Pack purchased on day 7 of grace versus day 8** — ACC-01's pack expires end of 2026-10-30; grace days 1–7 are 2026-10-31 … 2026-11-06. BUY_PACK on 2026-11-06 (day 7, commands.txt line 54) returns 8991860001815188447 to ACTIVE. ACC-03's pack also expires 2026-10-30 but its BUY_PACK comes on 2026-11-07 (day 8, line 55): all 15 ACC-03 SIMs become DEACTIVATED on 2026-11-07; three are re-registered and re-activated at lines 56–61; usage of the other twelve from 2026-11-07 onward must be rejected.

Extra traps (realistic things your validation should catch):

- **Usage before activation** — 8991860025145244106 is activated only on 2026-10-03 (commands.txt line 48); usage.csv line 59 dated 2026-10-02 must be rejected (NOT_ACTIVE).
- **Usage while suspended** — 8991860007297875347 is SUSPENDED 2026-10-10 … 2026-10-19 (lines 49 and 52); usage.csv lines 382 and 487 must be rejected. The second SUSPEND at line 50 is an invalid transition (error line).
- **Unknown pack type** — commands.txt line 53 BUY_PACK|ACC-03|PK-XL → error line, no pack added.
- **Duplicate usage row** — usage.csv line 1530 repeats (8991860003168976846, 2026-10-08), first copy at line 237; reject the duplicate.
- **Unknown ICCID** — usage.csv line 1531 refers to an ICCID that is not registered → error line.
- **Rounding of overage** — mb_used has one decimal; overage per SIM per day is rounded UP to a whole MB (for example 35.2 MB beyond the cap → 36 MB charged).

## What is NOT in this pack
Expected outputs are not provided for this set. Validate your engine with your own test suite against the rules in your brief (BR-01 … BR-07). A separate hidden input set with the same schema will be used at final evaluation; outputs are compared field-for-field, so follow the column formats above exactly in your own output.

## Output format expected at evaluation
Produce these files (CSV, header row, same conventions as above). Column order matters.

### pool_log.csv
One row per account per day from 2026-10-01 to 2026-11-14, ordered by date then account_id.

Columns in order: `date`, `account_id`, `pool_mb_start`, `accepted_mb`, `pool_mb_used`, `overage_mb`, `pool_mb_end`, `active_sims`, `account_state`

### statements.csv
One row per STATEMENT command.

Columns in order: `account_id`, `period_start`, `period_end`, `packs_bought`, `pack_cost_rs`, `pool_mb_used`, `overage_mb`, `overage_charge_rs`, `subtotal_rs`, `gst_rs`, `total_rs`

### sim_states.csv
Final state of every SIM after the last command, ordered by iccid.

Columns in order: `iccid`, `account_id`, `final_state`, `state_since`

### errors.csv
Rejected usage rows and commands.

Columns in order: `source`, `line_no`, `reason`
