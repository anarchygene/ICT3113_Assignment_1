# Accuracy: llama3.1:8b-instruct-q4_K_M

Overall: **61/80 = 76.2%**  
Output conformance: 80/80 = 100.0% (R7 needs >= 99.0%)  
Sequential single-request latency (ms): n 80, mean 30198.9, p50 25165.1, p95 67340.4, p99 108354.7, max 108354.7

| Category | n | Correct | Accuracy | R6 (>= 70%) |
|---|---:|---:|---:|---|
| Credit reporting | 19 | 14 | 73.7% | pass |
| Debt collection | 11 | 7 | 63.6% | FAIL |
| Mortgage | 7 | 5 | 71.4% | pass |
| Credit card | 6 | 6 | 100.0% | pass |
| Bank account or service | 14 | 10 | 71.4% | pass |
| Consumer loan | 8 | 5 | 62.5% | FAIL |
| Money transfer or service | 15 | 14 | 93.3% | pass |

## Confusion matrix (rows = golden, columns = predicted)

| golden \ predicted | CR | DC | Mtg | CC | Bank | Loan | MT | Invalid |
|---|---|---|---|---|---|---|---|---|
| CR | 14 | 2 | 0 | 2 | 1 | 0 | 0 | 0 |
| DC | 2 | 7 | 0 | 0 | 2 | 0 | 0 | 0 |
| Mtg | 0 | 0 | 5 | 1 | 0 | 1 | 0 | 0 |
| CC | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| Bank | 1 | 0 | 0 | 1 | 10 | 0 | 2 | 0 |
| Loan | 1 | 0 | 1 | 0 | 1 | 5 | 0 | 0 |
| MT | 0 | 0 | 0 | 1 | 0 | 0 | 14 | 0 |
