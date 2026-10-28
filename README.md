# MarketPulse AI — Search Trends & Market Intelligence

A Streamlit portfolio prototype for exploring search-interest trends, highlighting potential emerging products, and illustrating an automated data pipeline.

## Demo scope

- Market overview with KPI cards and interactive Plotly charts
- Keyword trend explorer with CSV export
- Emerging-product signals using a simple 3-month vs. prior 3-month comparison
- Pipeline monitor mock-up showing example workflow status and logs

## Important data note

**The current version uses simulated data.** Pipeline statuses and execution logs are illustrative, not evidence of live API calls or running scheduled workflows. The trend-growth heuristic is for demonstration and is not a predictive model.

## Run locally

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies and start Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Select **Create app**, choose this repository, branch `main`, and file `app.py`.
4. Deploy. No secrets are required for this sample-data version.

## Next steps toward production

1. Choose a provider and confirm historical coverage, rate limits, and costs.
2. Implement a provider adapter with timeouts, retries, and response validation.
3. Store observations in PostgreSQL with a uniqueness constraint such as `(provider, keyword, country, observation_date)`.
4. Add an n8n workflow to trigger collection and record execution results.
5. Keep credentials in deployment secrets; never commit `.env` files or API keys.
6. Replace illustrative pipeline statuses with actual job-run records.

## Suggested architecture

- **Streamlit:** interactive exploration and monitoring UI
- **Python:** ingestion, validation, and trend calculations
- **PostgreSQL:** historical observations and workflow runs
- **n8n:** scheduled orchestration and notifications
- **External provider APIs:** search and market data
