import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Salary Insights | UK Job Market", page_icon="bar_chart", layout="wide")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.db")

st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    h1 {font-size: 2.2rem !important; font-weight: 700 !important; margin-bottom: 0.2rem !important;}
    .subtitle {font-size: 1rem; color: #6b7280; margin-bottom: 2rem;}
    [data-testid="stMetric"] {background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;}
    [data-testid="stMetricLabel"] {font-size: 0.85rem !important;}
</style>
""", unsafe_allow_html=True)

BLUE = "#2563eb"
BLUE_SCALE = ["#dbeafe", "#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#1e40af"]
GREEN = "#059669"
GREEN_SCALE = ["#d1fae5", "#6ee7b7", "#34d399", "#10b981", "#059669", "#047857", "#065f46"]

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    jobs = pd.read_sql_query("SELECT * FROM jobs", conn)
    skills = pd.read_sql_query("SELECT * FROM job_skills", conn)
    conn.close()
    return jobs, skills

jobs, skills = load_data()

st.title("Salary Insights")

salary_jobs = jobs[jobs["salary_min"].notna() & jobs["salary_max"].notna()].copy()
salary_jobs["salary_mid"] = (salary_jobs["salary_min"] + salary_jobs["salary_max"]) / 2

st.markdown(f'<p class="subtitle">Analysing <strong>{len(salary_jobs)}</strong> out of {len(jobs)} jobs that include salary information ({round(len(salary_jobs)/len(jobs)*100,1)}%).</p>', unsafe_allow_html=True)

if len(salary_jobs) == 0:
    st.warning("No jobs with salary data found.")
    st.stop()

# Salary metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Median Salary (Min)", f"£{int(salary_jobs['salary_min'].median()):,}")
col2.metric("Median Salary (Max)", f"£{int(salary_jobs['salary_max'].median()):,}")
col3.metric("Highest Min Salary", f"£{int(salary_jobs['salary_min'].max()):,}")
col4.metric("Lowest Min Salary", f"£{int(salary_jobs['salary_min'].min()):,}")

st.markdown("")

# Salary distribution
st.subheader("Salary Distribution")
fig_dist = px.histogram(
    salary_jobs, x="salary_mid", nbins=30,
    labels={"salary_mid": "Salary (£)", "count": "Number of Jobs"},
    color_discrete_sequence=[BLUE]
)
fig_dist.update_layout(
    height=400, margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(size=13)
)
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("")
st.markdown("---")
st.markdown("")

# Salary by city
st.subheader("Salary by City")
city_salary = salary_jobs.groupby("location_display").agg(
    job_count=("job_id", "count"),
    avg_min=("salary_min", "mean"),
    avg_max=("salary_max", "mean"),
    median_mid=("salary_mid", "median")
).reset_index()

city_salary = city_salary[city_salary["job_count"] >= 3].sort_values("median_mid", ascending=False).head(10)

if len(city_salary) > 0:
    fig_city = go.Figure()
    fig_city.add_trace(go.Bar(
        name="Avg Min Salary",
        y=city_salary["location_display"],
        x=city_salary["avg_min"],
        orientation="h",
        marker_color=BLUE,
        text=[f"£{int(v):,}" for v in city_salary["avg_min"]],
        textposition="inside"
    ))
    fig_city.add_trace(go.Bar(
        name="Avg Max Salary",
        y=city_salary["location_display"],
        x=city_salary["avg_max"] - city_salary["avg_min"],
        orientation="h",
        marker_color=GREEN,
        text=[f"£{int(v):,}" for v in city_salary["avg_max"]],
        textposition="inside",
        base=city_salary["avg_min"]
    ))
    fig_city.update_layout(
        barmode="stack",
        yaxis=dict(autorange="reversed"),
        height=450, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13)
    )
    st.plotly_chart(fig_city, use_container_width=True)
    st.caption("Cities with at least 3 job postings including salary data.")
else:
    st.info("Not enough salary data per city for comparison.")

st.markdown("")
st.markdown("---")
st.markdown("")

# Salary by skill
st.subheader("Salary Premium by Skill")
st.markdown('<p class="subtitle">Does knowing a specific skill correlate with higher salaries?</p>', unsafe_allow_html=True)

skill_salary = []
for skill_name in skills["skill_name"].unique():
    skill_job_ids = skills[skills["skill_name"] == skill_name]["job_id"].unique()
    matching = salary_jobs[salary_jobs["job_id"].isin(skill_job_ids)]
    if len(matching) >= 2:
        skill_salary.append({
            "Skill": skill_name,
            "Jobs with Salary": len(matching),
            "Avg Min Salary": int(matching["salary_min"].mean()),
            "Avg Max Salary": int(matching["salary_max"].mean()),
            "Median Mid Salary": int(matching["salary_mid"].median())
        })

if skill_salary:
    skill_salary_df = pd.DataFrame(skill_salary).sort_values("Median Mid Salary", ascending=False)

    fig_skill_sal = px.bar(
        skill_salary_df, x="Skill", y="Median Mid Salary",
        text=[f"£{v:,}" for v in skill_salary_df["Median Mid Salary"]],
        color="Median Mid Salary",
        color_continuous_scale=BLUE_SCALE
    )
    fig_skill_sal.update_traces(textposition="outside")
    fig_skill_sal.update_layout(
        showlegend=False, coloraxis_showscale=False,
        height=450, margin=dict(l=0, r=0, t=10, b=0),
        xaxis_tickangle=-45,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13)
    )
    st.plotly_chart(fig_skill_sal, use_container_width=True)
    st.caption("Skills with at least 2 job postings including salary data.")

    st.markdown("")

    st.dataframe(
        skill_salary_df.style.format({
            "Avg Min Salary": "£{:,.0f}",
            "Avg Max Salary": "£{:,.0f}",
            "Median Mid Salary": "£{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Not enough salary data across skills for comparison.")

# Footer
st.markdown("---")
st.markdown(
    f'<p style="font-size: 0.8rem; color: #9ca3af;">Note: Only {len(salary_jobs)} of {len(jobs)} jobs ({round(len(salary_jobs)/len(jobs)*100,1)}%) '
    f'include salary information. Results should be interpreted with this in mind. &nbsp;|&nbsp; Built by Munib Ahmed</p>',
    unsafe_allow_html=True
)