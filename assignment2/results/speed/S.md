# S measurement, Llama alone, 2026-11-26T11:59:43Z
CASCADE_ENABLED=false
CASCADE_ESCALATE_ON=Credit reporting,Credit card,Bank account or service,Consumer loan,Money transfer or service,Debt collection
CASCADE_LABEL=
CASCADE_LARGE_MODEL=llama3.1:8b-instruct-q4_K_M
CASCADE_SMALL_MODEL=gemma3:1b-it-q4_K_M
OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
warm-up row 9716: HTTP 201 Consumer loan 19.4 s (discarded)
warm-up row 9438: HTTP 201 Credit reporting 8.5 s (discarded)
warm-up row 9775: HTTP 201 Credit reporting 13.1 s (discarded)
row 9094 (137 words): 12.61 s -> Credit reporting
row 9108 (137 words): 10.51 s -> Consumer loan
row 9246 (137 words): 11.05 s -> Bank account or service

```json
{
  "measured_utc": "2026-11-26T12:00:58Z",
  "rows": [
    9094,
    9108,
    9246
  ],
  "timings_s": [
    12.61,
    10.51,
    11.05
  ],
  "S_s": 11.05,
  "interval_s": 22.1,
  "rate_per_min": 2.7149,
  "rate_per_hour": 162.9,
  "run_min": 11.05,
  "response_timeout_s": 300.0,
  "pause_min": 6.0,
  "expected_tickets_per_run": 30.0,
  "client_peak_per_hour": {
    "A1 peak": 81,
    "A1 peak + 30% headroom": 105
  }
}
```
