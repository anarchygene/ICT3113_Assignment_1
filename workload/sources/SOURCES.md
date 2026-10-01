# Step 3 source evidence

All checks done 1 Oct 2026. "Human-verified" means a team member opened the source and saw the number directly.

| ID | Figure | Value | Source | Location | Evidence file | Status |
|---|---|---|---|---|---|---|
| S1 | CFPB complaints received, 2023 | ~1,657,600 | CFPB Consumer Response Annual Report 2023 | PDF p.5 of 81 (intro) | `cfpb-annual-report-2023_pdf-p5_total-1657600.png` | Human-verified (Yekai) |
| S2 | CFPB complaints received, 2024 | ~3,187,900 | CFPB Consumer Response Annual Report 2024 | PDF p.5 of 95 (intro) | `cfpb-annual-report-2024_pdf-p5_total-3187900.png` | Human-verified (Yekai) |
| S1b | CFPB 2023: received / sent to companies | ~1,657,600 / ~1,348,200 (81%) | CFPB Consumer Response Annual Report 2023 | PDF p.9: "Of the approximately 1,657,600 complaints the CFPB received in 2023, it sent about 1,348,200 (81%) to companies for review and response…" | `cfpb-annual-report-2023_pdf-p9_received-and-sent.png` | Human-verified (Yekai) |
| S2b | CFPB 2024: received / sent to companies | ~3,187,900 / ~2,829,400 (89%) | CFPB Consumer Response Annual Report 2024 | PDF p.9: "Of the approximately 3,187,900 complaints the CFPB received in 2024, it sent approximately 2,829,400 (or 89%) to companies for review and response…" | `cfpb-annual-report-2024_pdf-p9_received-and-sent.png` | Human-verified (Yekai) |
| S3 | CFPB complaints, all companies, Mon 2 Oct 2023 | 4,290 | CFPB Consumer Complaint Database API | [query](https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-02&date_received_max=2023-10-02&size=0&no_aggs=true) | `api/cfpb_all_2023-10-02.json` | Human-verified (Yekai) + re-fetched |
| S4 | CFPB complaints, KEYCORP, 2024 | 620 | CFPB Consumer Complaint Database API | [query](https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=KEYCORP) | `api/cfpb_keycorp_2024.json` | Human-verified (Yekai) + re-fetched |
| S5 | UK firms' complaints received, 2025 H2 | 1.74m (2025 H1: 1.83m) | FCA aggregate complaints data, 2025 H2 | Key Findings: "In 2025 H2, financial services firms received 1.74m complaints… Since 2021 H1, complaints have stayed relatively constant between 1.7m and 2.0m." | `fca-aggregate-complaints-2025H2_key-findings_1.74m.png` | Human-verified (Yekai) |
| S6 | Barclays Bank UK PLC complaints opened, H1 2026 | 94,535 (Banking and Credit Cards 85,021) | Barclays UK complaints data, Jan–Jun 2026 | "Barclays Bank UK PLC" table (firm name BBUKPLC shown), "Total" row | `barclays-uk-complaints-2026H1_bbukplc-table_94535.png` | Human-verified (Yekai) |
| S7 | FIDReC claims against banks and finance companies | 1,387 → 1,831 (+32%) | FIDReC news, 26 Nov 2025, [KA-01328](https://www.fidrec.com.sg/knowledgebase/article/KA-01328/en-us) | "Disputes rose across most FI categories": "Banks and finance companies: 1,831 claims, up from 1,387." | `fidrec-2025-annual_banks-finance-1387-to-1831.png` | Human-verified (Yekai) |

API responses report `last_updated: 2026-10-01T12:00:00-05:00`. The database updates daily, so counts can change slightly if re-run later.

## Not used

- `fca-financial-lives-2024_pdf-p63_debt-advice_NOT-USED.png`: FCA Financial Lives 2024, PDF p.63, on debt-advice usage (1.7M adults). It does not support any workload figure. The figures we need from the FCA are the H2 2025 aggregate complaints total (1.74M) and the "4% of investment-product holders complained" finding (key findings p.16).

## TODO

- PDF and page URLs are listed in `../research-notes.md` §12.
- Note: FCA's text says "a 0.4% decrease" from 1.83m to 1.74m, but that's actually about 4.9%. Cite only the 1.74m figure, not the percentage.
