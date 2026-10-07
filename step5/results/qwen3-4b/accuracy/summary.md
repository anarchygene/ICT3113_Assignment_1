# Accuracy: qwen3:4b-instruct-2507-q4_K_M

Overall: **110/160 = 68.8%** (R5 needs >= 136/160)  
Output conformance: 157/160 = 98.1% (R7 needs >= 99.0%)  
Sequential single-request latency (ms): n 157, mean 7894.1, p50 7916.9, p95 14015.5, p99 16329.1, max 16686.6

| Category | n | Correct | Accuracy | R6 (>= 70%) |
|---|---:|---:|---:|---|
| Credit reporting | 33 | 17 | 51.5% | FAIL |
| Debt collection | 24 | 15 | 62.5% | FAIL |
| Mortgage | 18 | 15 | 83.3% | pass |
| Credit card | 11 | 10 | 90.9% | pass |
| Bank account or service | 30 | 20 | 66.7% | FAIL |
| Consumer loan | 16 | 13 | 81.2% | pass |
| Money transfer or service | 28 | 20 | 71.4% | pass |

## Confusion matrix (rows = golden, columns = predicted)

| golden \ predicted | CR | DC | Mtg | CC | Bank | Loan | MT | Invalid |
|---|---|---|---|---|---|---|---|---|
| CR | 17 | 4 | 0 | 9 | 1 | 2 | 0 | 0 |
| DC | 2 | 15 | 0 | 1 | 2 | 4 | 0 | 0 |
| Mtg | 0 | 1 | 15 | 0 | 0 | 2 | 0 | 0 |
| CC | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 1 |
| Bank | 0 | 1 | 0 | 5 | 20 | 1 | 2 | 1 |
| Loan | 0 | 0 | 1 | 0 | 1 | 13 | 0 | 1 |
| MT | 0 | 0 | 0 | 3 | 5 | 0 | 20 | 0 |
