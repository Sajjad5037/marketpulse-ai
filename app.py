import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import date

st.set_page_config(page_title="MarketPulse AI", page_icon="📈", layout="wide")

# ---------- Demo data (clearly simulated) ----------
@st.cache_data
def make_demo_data():
    rng = np.random.default_rng(17)
    keywords = [
        ("Smart rings", "Wearables", "United States"),
        ("Portable solar generator", "Clean Energy", "United States"),
        ("Matcha powder", "Food & Beverage", "United Kingdom"),
        ("Electric bike", "Mobility", "Australia"),
        ("AI note taker", "Productivity", "Canada"),
        ("Standing desk", "Office", "United Kingdom"),
        ("Home battery", "Clean Energy", "Australia"),
        ("Noise cancelling earbuds", "Electronics", "Canada"),
        ("Red light therapy mask", "Beauty", "United States"),
        ("Robot lawn mower", "Smart Home", "Australia"),
        ("Reusable water filter", "Home", "United Kingdom"),
        ("Smart pet feeder", "Smart Home", "Canada"),
    ]
    months = pd.date_range(end=pd.Timestamp.today().normalize().replace(day=1), periods=18, freq="MS")
    rows = []
    for i, (keyword, category, country) in enumerate(keywords):
        base = rng.integers(30, 100)
        slope = rng.uniform(-1.0, 5.0)
        for j, month in enumerate(months):
            seasonal = 8 * np.sin(j / 2.4 + i)
            value = max(5, base + slope*j + seasonal + rng.normal(0, 5))
            rows.append({
                "keyword": keyword,
                "category": category,
                "country": country,
                "month": month,
                "search_index": round(float(min(100, value)), 1),
                "estimated_searches": int(max(0, value * rng.integers(80, 180))),
            })
    return pd.DataFrame(rows)

df = make_demo_data()
latest_month = df["month"].max()
previous_month = df.loc[df["month"] < latest_month, "month"].max()

# Sidebar
st.sidebar.markdown("## 📈 MarketPulse AI")
st.sidebar.caption("Search-trend intelligence · Demo")
page = st.sidebar.radio("Navigate", ["Overview", "Trend Explorer", "Emerging Products", "Pipeline Monitor"])
st.sidebar.divider()
st.sidebar.caption("⚠️ Demo mode: all displayed data is simulated.")
country_options = ["All countries"] + sorted(df["country"].unique().tolist())
selected_country = st.sidebar.selectbox("Country filter", country_options)
category_options = ["All categories"] + sorted(df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Category filter", category_options)

filtered = df.copy()
if selected_country != "All countries":
    filtered = filtered[filtered["country"] == selected_country]
if selected_category != "All categories":
    filtered = filtered[filtered["category"] == selected_category]

# Calculate growth over latest 3 months vs previous 3 months
def growth_table(data):
    months = sorted(data["month"].unique())
    if len(months) < 6:
        return pd.DataFrame(columns=["keyword", "category", "country", "recent_avg", "prior_avg", "growth_pct"])
    recent, prior = months[-3:], months[-6:-3]
    agg = data.groupby(["keyword", "category", "country", "month"], as_index=False)["search_index"].mean()
    r = agg[agg.month.isin(recent)].groupby(["keyword","category","country"], as_index=False).search_index.mean().rename(columns={"search_index":"recent_avg"})
    p = agg[agg.month.isin(prior)].groupby(["keyword","category","country"], as_index=False).search_index.mean().rename(columns={"search_index":"prior_avg"})
    out = r.merge(p, on=["keyword","category","country"], how="left")
    out["growth_pct"] = np.where(out["prior_avg"] > 0, (out["recent_avg"] - out["prior_avg"]) / out["prior_avg"] * 100, np.nan)
    return out.sort_values("growth_pct", ascending=False)

growth = growth_table(filtered)

def heading(title, subtitle):
    st.title(title)
    st.caption(subtitle)

if page == "Overview":
    heading("Market intelligence overview", "A prototype for collecting search signals and spotting emerging products.")
    st.info("This interactive prototype uses simulated data. Connect a provider API to replace sample values with real observations.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tracked keywords", f"{filtered['keyword'].nunique():,}", "Across selected filters")
    c2.metric("Countries monitored", f"{filtered['country'].nunique():,}")
    rising = int((growth["growth_pct"] >= 20).sum()) if not growth.empty else 0
    c3.metric("Fast-rising signals", f"{rising:,}", "≥20% recent growth")
    c4.metric("Collection success", "98.5%", "Illustrative demo metric")
    st.divider()
    left, right = st.columns([1.7, 1])
    with left:
        st.subheader("Search interest over time")
        chosen = st.selectbox("Choose a keyword", sorted(filtered["keyword"].unique()))
        trend = filtered[filtered["keyword"] == chosen]
        fig = px.line(trend, x="month", y="search_index", markers=True,
                      labels={"month":"Month", "search_index":"Search interest index"},
                      title=chosen)
        fig.update_layout(margin=dict(l=10,r=10,t=50,b=10), height=350, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Category signals")
        cat = filtered.groupby("category", as_index=False)["search_index"].mean().sort_values("search_index", ascending=True)
        fig2 = px.bar(cat, x="search_index", y="category", orientation="h",
                      labels={"search_index":"Avg. interest index","category":""})
        fig2.update_layout(margin=dict(l=5,r=5,t=15,b=5), height=350)
        st.plotly_chart(fig2, use_container_width=True)
    st.subheader("Latest observations")
    latest = filtered[filtered["month"] == latest_month][["keyword","category","country","search_index","estimated_searches"]]
    st.dataframe(latest.sort_values("search_index", ascending=False), use_container_width=True, hide_index=True)

elif page == "Trend Explorer":
    heading("Trend explorer", "Compare keyword interest and explore the history behind a signal.")
    keywords = sorted(filtered["keyword"].unique())
    chosen = st.multiselect("Keywords to compare", keywords, default=keywords[:min(3, len(keywords))])
    chart_data = filtered[filtered["keyword"].isin(chosen)]
    if chart_data.empty:
        st.warning("Select at least one keyword to display a trend.")
    else:
        fig = px.line(chart_data, x="month", y="search_index", color="keyword", markers=True,
                      labels={"month":"Month","search_index":"Search interest index","keyword":"Keyword"})
        fig.update_layout(height=470, hovermode="x unified", margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Index values are simulated and intended only to demonstrate the interaction pattern.")
        st.download_button("Download selected observations (CSV)", chart_data.to_csv(index=False).encode("utf-8"),
                           file_name="marketpulse_trend_observations.csv", mime="text/csv")

elif page == "Emerging Products":
    heading("Emerging product signals", "A transparent baseline comparison to prioritize keywords for further research.")
    st.caption("Growth compares the most recent 3 months with the preceding 3 months. This is a simple heuristic, not a prediction.")
    threshold = st.slider("Minimum growth threshold (%)", min_value=0, max_value=100, value=20, step=5)
    if growth.empty:
        st.warning("Not enough history under the selected filters.")
    else:
        results = growth[growth["growth_pct"] >= threshold].copy()
        results["growth_pct"] = results["growth_pct"].map(lambda x: f"{x:.1f}%")
        st.metric("Signals meeting threshold", len(results))
        st.dataframe(results.rename(columns={
            "keyword":"Keyword", "category":"Category", "country":"Country",
            "recent_avg":"Recent 3-month avg.", "prior_avg":"Previous 3-month avg.",
            "growth_pct":"Growth"
        }), use_container_width=True, hide_index=True)
        st.download_button("Export emerging signals (CSV)", results.to_csv(index=False).encode("utf-8"),
                           file_name="marketpulse_emerging_signals.csv", mime="text/csv")
    st.subheader("How the signal is calculated")
    st.code("growth_pct = (recent_3_month_average - previous_3_month_average) / previous_3_month_average * 100", language="python")

else:
    heading("Pipeline monitor", "Illustrative operational view for a future Python + PostgreSQL + n8n pipeline.")
    st.warning("Workflow statuses below are simulated. No live API requests or scheduled jobs are running in this demo.")
    jobs = pd.DataFrame([
        {"Workflow":"Keyword history collection","Provider":"Data provider (demo)","Last run":"Today · 09:00","Records":"216","Status":"Success","Duration":"8.4 s"},
        {"Workflow":"Market price refresh","Provider":"EODHD (demo)","Last run":"Today · 08:55","Records":"48","Status":"Success","Duration":"3.1 s"},
        {"Workflow":"Emerging trend calculation","Provider":"Python analysis","Last run":"Today · 08:15","Records":"12","Status":"Success","Duration":"1.2 s"},
        {"Workflow":"WordPress content sync","Provider":"WordPress (demo)","Last run":"Yesterday · 18:00","Records":"—","Status":"Not configured","Duration":"—"},
    ])
    st.dataframe(jobs, use_container_width=True, hide_index=True)
    st.subheader("Example execution log")
    st.code("""09:00:00  INFO   Workflow started
09:00:01  INFO   Loaded keyword configuration
09:00:03  INFO   Provider request completed (simulated)
09:00:04  INFO   Validated response schema
09:00:05  INFO   Upserted historical observations (simulated)
09:00:06  INFO   Workflow completed""", language="text")
    st.subheader("Production-readiness checklist")
    st.checkbox("Provider credentials stored as deployment secrets", value=False, disabled=True)
    st.checkbox("Retry policy and request timeouts configured", value=False, disabled=True)
    st.checkbox("Database uniqueness constraints prevent duplicate observations", value=False, disabled=True)
    st.checkbox("Monitoring and failure notifications configured", value=False, disabled=True)

st.sidebar.divider()
st.sidebar.caption("Built as a portfolio proof of concept.")
