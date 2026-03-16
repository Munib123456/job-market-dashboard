import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="UK Job Market Intelligence", page_icon="bar_chart", layout="wide")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.db")

# Custom CSS for cleaner look
st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    h1 {font-size: 2.2rem !important; font-weight: 700 !important; margin-bottom: 0.2rem !important;}
    .subtitle {font-size: 1rem; color: #6b7280; margin-bottom: 2rem;}
    .footer-text {font-size: 0.8rem; color: #9ca3af; margin-top: 1rem;}
    [data-testid="stMetric"] {background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;}
    [data-testid="stMetricLabel"] {font-size: 0.85rem !important;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    jobs = pd.read_sql_query("SELECT * FROM jobs", conn)
    skills = pd.read_sql_query("SELECT * FROM job_skills", conn)
    conn.close()
    return jobs, skills

jobs, skills = load_data()

# Header
st.title("UK Job Market Intelligence Dashboard")
st.markdown('<p class="subtitle">Tracking skill demand, salary trends, and hiring patterns across UK data analyst and business analyst roles. Data sourced from the Adzuna API.</p>', unsafe_allow_html=True)

# Headline metrics
total_jobs = len(jobs)
unique_companies = jobs["company"].nunique()
jobs_with_salary = jobs[jobs["salary_min"].notna()]
avg_salary_min = int(jobs_with_salary["salary_min"].mean()) if len(jobs_with_salary) > 0 else 0
avg_salary_max = int(jobs_with_salary["salary_max"].mean()) if len(jobs_with_salary) > 0 else 0

if len(skills) > 0:
    top_skill = skills["skill_name"].value_counts().index[0]
    top_skill_count = skills["skill_name"].value_counts().values[0]
    top_skill_pct = round(top_skill_count / total_jobs * 100, 1)
else:
    top_skill = "N/A"
    top_skill_pct = 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs Tracked", f"{total_jobs:,}")
col2.metric("Unique Companies", f"{unique_companies:,}")
col3.metric("Most In-Demand Skill", f"{top_skill} ({top_skill_pct}%)")
col4.metric("Avg Salary Range", f"£{avg_salary_min:,} - £{avg_salary_max:,}")

st.markdown("")
st.markdown("")

# Colour palette
BLUE = "#2563eb"
GREEN = "#059669"
BLUE_SCALE = ["#dbeafe", "#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#1e40af"]
GREEN_SCALE = ["#d1fae5", "#6ee7b7", "#34d399", "#10b981", "#059669", "#047857", "#065f46"]

# Two charts side by side
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Top 15 In-Demand Skills")
    if len(skills) > 0:
        skill_counts = skills["skill_name"].value_counts().head(15).reset_index()
        skill_counts.columns = ["Skill", "Count"]
        skill_counts["Percentage"] = round(skill_counts["Count"] / total_jobs * 100, 1)
        fig_skills = px.bar(
            skill_counts, x="Count", y="Skill", orientation="h",
            text="Percentage", color="Count",
            color_continuous_scale=BLUE_SCALE
        )
        fig_skills.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_skills.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False, coloraxis_showscale=False,
            height=500, margin=dict(l=0, r=50, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=13)
        )
        st.plotly_chart(fig_skills, use_container_width=True)

with right_col:
    st.subheader("Top 10 Cities by Job Volume")
    city_counts = jobs["location_display"].value_counts().head(10).reset_index()
    city_counts.columns = ["City", "Jobs"]
    fig_cities = px.bar(
        city_counts, x="Jobs", y="City", orientation="h",
        text="Jobs", color="Jobs",
        color_continuous_scale=GREEN_SCALE
    )
    fig_cities.update_traces(textposition="outside")
    fig_cities.update_layout(
        yaxis=dict(autorange="reversed"),
        showlegend=False, coloraxis_showscale=False,
        height=500, margin=dict(l=0, r=50, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13)
    )
    st.plotly_chart(fig_cities, use_container_width=True)

st.markdown("")

# Skills by category
st.subheader("Skills Breakdown by Category")
if len(skills) > 0:
    category_skill = skills.groupby(["skill_category", "skill_name"]).size().reset_index(name="Count")
    fig_treemap = px.treemap(
        category_skill, path=["skill_category", "skill_name"],
        values="Count", color="Count",
        color_continuous_scale=BLUE_SCALE
    )
    fig_treemap.update_layout(
        height=450, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f'<p class="footer-text">Data source: Adzuna API &nbsp;|&nbsp; Jobs tracked: {total_jobs} &nbsp;|&nbsp; '
    f'Jobs with salary data: {len(jobs_with_salary)} &nbsp;|&nbsp; '
    f'Jobs with identifiable skills: {skills["job_id"].nunique() if len(skills) > 0 else 0} &nbsp;|&nbsp; '
    f'Built by Munib Ahmed</p>',
    unsafe_allow_html=True
)