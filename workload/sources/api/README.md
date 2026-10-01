# CFPB API responses

Raw, unedited responses from the CFPB Consumer Complaint Database API, saved as evidence. The database updates daily, so re-running a query later may return a slightly different count.

Retrieved 1 Oct 2026. Each response's `_meta.last_updated` is `2026-10-01T12:00:00-05:00`.

| File | Query | Count (`hits.total.value`) | Used for |
|---|---|---|---|
| `cfpb_all_2023-10-02.json` | All companies, date received 2 Oct 2023: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-02&date_received_max=2023-10-02&size=0&no_aggs=true | 4,290 | Weekday pattern (WORKLOAD.md §2), source S3 |
| `cfpb_keycorp_2024.json` | KEYCORP, date received 1 Jan – 31 Dec 2024: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=KEYCORP | 620 | CFPB per-company scale (WORKLOAD.md §1), source S4 |

To reproduce: open the query URL in a browser, or run `curl -s "<URL>"`.
