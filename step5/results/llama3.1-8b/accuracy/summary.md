# Accuracy: llama3.1:8b-instruct-q4_K_M

Overall: **121/160 = 75.6%** (R5 needs >= 136/160)  
Output conformance: 159/160 = 99.4% (R7 needs >= 99.0%)  
Sequential single-request latency (ms): n 159, mean 13815.6, p50 13228.7, p95 25592.4, p99 29258.3, max 30239.2

| Category | n | Correct | Accuracy | R6 (>= 70%) |
|---|---:|---:|---:|---|
| Credit reporting | 33 | 23 | 69.7% | FAIL |
| Debt collection | 24 | 18 | 75.0% | pass |
| Mortgage | 18 | 15 | 83.3% | pass |
| Credit card | 11 | 11 | 100.0% | pass |
| Bank account or service | 30 | 20 | 66.7% | FAIL |
| Consumer loan | 16 | 11 | 68.8% | FAIL |
| Money transfer or service | 28 | 23 | 82.1% | pass |

## Confusion matrix (rows = golden, columns = predicted)

| golden \ predicted | CR | DC | Mtg | CC | Bank | Loan | MT | Invalid |
|---|---|---|---|---|---|---|---|---|
| CR | 23 | 3 | 0 | 5 | 2 | 0 | 0 | 0 |
| DC | 2 | 18 | 0 | 2 | 2 | 0 | 0 | 0 |
| Mtg | 0 | 0 | 15 | 2 | 0 | 1 | 0 | 0 |
| CC | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 |
| Bank | 1 | 2 | 0 | 3 | 20 | 0 | 4 | 0 |
| Loan | 1 | 0 | 1 | 1 | 1 | 11 | 0 | 1 |
| MT | 0 | 0 | 0 | 3 | 2 | 0 | 23 | 0 |
