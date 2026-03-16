import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="UK Job Market Intelligence", page_icon="📊", layout="wide")

# Database connection
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.db")

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    jobs = pd.read_sql_query("SELECT * FROM jobs", conn)
    skills = pd.read_sql_query("SELECT * FROM job_skills", conn)
    conn.close()
    return jobs, skills

jobs, skills = load_data()

# Title
st.title("📊 UK Job Market Intelligence Dashboard")
st.markdown("Real-time analysis of UK data analyst and business analyst job postings. Data collected from the Adzuna API.")

# Headline metrics
total_jobs = len(jobs)
unique_companies = jobs["company"].nunique()
jobs_with_salary = jobs[jobs["salary_min"].notna()]
avg_salary_min = int(jobs_with_salary["salary_min"].mean()) if len(jobs_with_salary) > 0 else 0
avg_salary_max = int(jobs_with_salary["salary_max"].mean()) if len(jobs_with_salary) > 0 else 0

# Top skill
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

st.markdown("---")

# Two charts side by side
left_col, right_col = st.columns(2)

# Top 15 skills bar chart
with left_col:
    st.subheader("Top 15 In-Demand Skills")
    if len(skills) > 0:
        skill_counts = skills["skill_name"].value_counts().head(15).reset_index()
        skill_counts.columns = ["Skill", "Count"]
        skill_counts["Percentage"] = round(skill_counts["Count"] / total_jobs * 100, 1)
        fig_skills = px.bar(
            skill_counts,
            x="Count",
            y="Skill",
            orientation="h",
            text="Percentage",
            color="Count",
            color_continuous_scale="blues"
        )
        fig_skills.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_skills.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            coloraxis_showscale=False,
            height=500,
            margin=dict(l=0, r=40, t=10, b=0)
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("No skill data available.")

# Jobs by city
with right_col:
    st.subheader("Top 10 Cities by Job Volume")
    city_counts = jobs["location_display"].value_counts().head(10).reset_index()
    city_counts.columns = ["City", "Jobs"]
    fig_cities = px.bar(
        city_counts,
        x="Jobs",
        y="City",
        orientation="h",
        text="Jobs",
        color="Jobs",
        color_continuous_scale="greens"
    )
    fig_cities.update_traces(textposition="outside")
    fig_cities.update_layout(
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        coloraxis_showscale=False,
        height=500,
        margin=dict(l=0, r=40, t=10, b=0)
    )
    st.plotly_chart(fig_cities, use_container_width=True)

st.markdown("---")

# Skills by category breakdown
st.subheader("Skills Breakdown by Category")
if len(skills) > 0:
    category_skill = skills.groupby(["skill_category", "skill_name"]).size().reset_index(name="Count")
    fig_treemap = px.treemap(
        category_skill,
        path=["skill_category", "skill_name"],
        values="Count",
        color="Count",
        color_continuous_scale="blues"
    )
    fig_treemap.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_treemap, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f"**Data source:** Adzuna API | **Jobs tracked:** {total_jobs} | "
    f"**Jobs with salary data:** {len(jobs_with_salary)} | "
    f"**Jobs with identifiable skills:** {skills['job_id'].nunique() if len(skills) > 0 else 0}"
)