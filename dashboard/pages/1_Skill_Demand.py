import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Skill Demand | UK Job Market", page_icon="📊", layout="wide")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.db")

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    jobs = pd.read_sql_query("SELECT * FROM jobs", conn)
    skills = pd.read_sql_query("SELECT * FROM job_skills", conn)
    conn.close()
    return jobs, skills

jobs, skills = load_data()
total_jobs = len(jobs)

st.title("🔍 Skill Demand Analysis")
st.markdown("Explore which skills UK employers are asking for in data and business analyst roles.")

if len(skills) == 0:
    st.warning("No skill data available.")
    st.stop()

# Get all unique skills sorted by frequency
all_skills = skills["skill_name"].value_counts()

st.markdown("---")

# Skill deep dive
st.subheader("Skill Deep Dive")
selected_skill = st.selectbox("Select a skill to explore:", all_skills.index.tolist())

if selected_skill:
    skill_jobs = skills[skills["skill_name"] == selected_skill]["job_id"].unique()
    matching_jobs = jobs[jobs["job_id"].isin(skill_jobs)]

    col1, col2, col3 = st.columns(3)

    mention_count = len(skill_jobs)
    mention_pct = round(mention_count / total_jobs * 100, 1)
    col1.metric(f"Jobs mentioning {selected_skill}", f"{mention_count} ({mention_pct}%)")

    salary_jobs = matching_jobs[matching_jobs["salary_min"].notna()]
    if len(salary_jobs) > 0:
        avg_min = int(salary_jobs["salary_min"].mean())
        avg_max = int(salary_jobs["salary_max"].mean())
        col2.metric("Avg Salary (with this skill)", f"£{avg_min:,} - £{avg_max:,}")
    else:
        col2.metric("Avg Salary (with this skill)", "No salary data")

    top_city = matching_jobs["location_display"].value_counts()
    if len(top_city) > 0:
        col3.metric("Top City", f"{top_city.index[0]} ({top_city.values[0]} jobs)")

    # City breakdown for this skill
    if len(matching_jobs) > 0:
        city_breakdown = matching_jobs["location_display"].value_counts().head(8).reset_index()
        city_breakdown.columns = ["City", "Jobs"]
        fig_city = px.bar(
            city_breakdown, x="Jobs", y="City", orientation="h",
            title=f"Where is {selected_skill} most demanded?",
            color="Jobs", color_continuous_scale="blues"
        )
        fig_city.update_layout(
            yaxis=dict(autorange="reversed"),
            showlegend=False, coloraxis_showscale=False,
            height=350, margin=dict(l=0, r=20, t=40, b=0)
        )
        st.plotly_chart(fig_city, use_container_width=True)

st.markdown("---")

# Skill comparison
st.subheader("Compare Skills Side by Side")
compare_skills = st.multiselect(
    "Select 2-5 skills to compare:",
    all_skills.index.tolist(),
    default=all_skills.index.tolist()[:3]
)

if len(compare_skills) >= 2:
    compare_data = []
    for skill in compare_skills:
        skill_job_ids = skills[skills["skill_name"] == skill]["job_id"].unique()
        matching = jobs[jobs["job_id"].isin(skill_job_ids)]
        salary_data = matching[matching["salary_min"].notna()]
        avg_salary = int(salary_data["salary_min"].mean()) if len(salary_data) > 0 else 0
        compare_data.append({
            "Skill": skill,
            "Job Count": len(skill_job_ids),
            "Percentage": round(len(skill_job_ids) / total_jobs * 100, 1),
            "Avg Min Salary": avg_salary
        })
    compare_df = pd.DataFrame(compare_data)

    left, right = st.columns(2)

    with left:
        fig_compare = px.bar(
            compare_df, x="Skill", y="Percentage",
            title="% of Jobs Requiring Each Skill",
            text="Percentage", color="Percentage",
            color_continuous_scale="blues"
        )
        fig_compare.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_compare.update_layout(
            showlegend=False, coloraxis_showscale=False,
            height=400, margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_compare, use_container_width=True)

    with right:
        salary_df = compare_df[compare_df["Avg Min Salary"] > 0]
        if len(salary_df) > 0:
            fig_salary = px.bar(
                salary_df, x="Skill", y="Avg Min Salary",
                title="Avg Minimum Salary by Skill",
                text="Avg Min Salary", color="Avg Min Salary",
                color_continuous_scale="greens"
            )
            fig_salary.update_traces(texttemplate="£%{text:,}", textposition="outside")
            fig_salary.update_layout(
                showlegend=False, coloraxis_showscale=False,
                height=400, margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig_salary, use_container_width=True)
        else:
            st.info("No salary data available for selected skills.")

elif len(compare_skills) == 1:
    st.info("Select at least 2 skills to compare.")

st.markdown("---")

# Category breakdown
st.subheader("Skills by Category")
category_counts = skills.groupby("skill_category")["job_id"].count().reset_index()
category_counts.columns = ["Category", "Total Mentions"]
category_counts = category_counts.sort_values("Total Mentions", ascending=False)

fig_cat = px.bar(
    category_counts, x="Category", y="Total Mentions",
    color="Total Mentions", color_continuous_scale="blues",
    text="Total Mentions"
)
fig_cat.update_traces(textposition="outside")
fig_cat.update_layout(
    showlegend=False, coloraxis_showscale=False,
    height=400, margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig_cat, use_container_width=True)