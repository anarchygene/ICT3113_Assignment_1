# A2 speed-test workload (brief Step 4)

Fixed before the first speed run. Not edited afterwards; regenerate only to check it
(`python assignment2/scripts/make_speed_workload.py` reproduces both files byte for byte).

| File | What | Used by |
|---|---|---|
| `speed_tickets.tsv` | 60 tickets, in send order, `row<TAB>body` (same format as A1's `tickets_load.tsv`) | JMeter: `-Jtickets_file=assignment2/workload/speed_tickets.tsv` |
| `warmup_tickets.tsv` | 3 warm-up tickets (rows 9716, 9438, 9775), same for every run | `POST /tickets`, one at a time, before each run (`STEP2.md` §7 step 1); timings discarded |

- **Rows 9000–9839 only.** No golden rows (9840–9999, the test and tuning sets), and no warm-up row is in the
  workload. The script asserts all three.
- **Text** is copied unchanged from `step5/data/tickets_load.tsv`, the A1 load-test source.
- **Length mix** (words, over the 840 rows): typical = p25–p75 (88–208 words), long = ≥ p90 (276+ words).
  48 typical + 12 long; every 5th ticket is long, so a ~30-ticket run gets 6 long tickets at the same positions.
  The warm-up tickets are typical (94–139 words).
- **Size.** At S ≈ 13 s (one ticket every 26 s) a 13-minute run needs about 30 tickets; 60 leaves room for
  Poisson variation and a smaller S. Every run starts from the top, so all runs send the same tickets in the
  same order. The A1 plan has `recycle=true`. If a run sends more than 60, the list repeats; report that.
- Selection is a seeded shuffle (seed 3113), not a hand pick.
