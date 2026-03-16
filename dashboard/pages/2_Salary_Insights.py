import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Salary Insights | UK Job Market", page_icon="📊", layout="wide")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.db")

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    jobs = pd.read_sql_query("SELECT * FROM jobs", conn)
    skills = pd.read_sql_query("SELECT * FROM job_skills", conn)
    conn.close()
    return jobs, skills

jobs, skills = load_data()

st.title("💰 Salary Insights")

# Filter to jobs with salary data
salary_jobs = jobs[jobs["salary_min"].notna() & jobs["salary_max"].notna()].copy()
salary_jobs["salary_mid"] = (salary_jobs["salary_min"] + salary_jobs["salary_max"]) / 2

st.markdown(f"Analysing **{len(salary_jobs)}** out of {len(jobs)} jobs that include salary information ({round(len(salary_jobs)/len(jobs)*100,1)}%).")

if len(salary_jobs) == 0:
    st.warning("No jobs with salary data found.")
    st.stop()

st.markdown("---")

# Salary distribution
st.subheader("Salary Distribution")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Median Salary (Min)", f"£{int(salary_jobs['salary_min'].median()):,}")
col2.metric("Median Salary (Max)", f"£{int(salary_jobs['salary_max'].median()):,}")
col3.metric("Highest Min Salary", f"£{int(salary_jobs['salary_min'].max()):,}")
col4.metric("Lowest Min Salary", f"£{int(salary_jobs['salary_min'].min()):,}")

fig_dist = px.histogram(
    salary_jobs, x="salary_mid", nbins=30,
    title="Distribution of Mid-Point Salaries",
    labels={"salary_mid": "Salary (£)", "count": "Number of Jobs"},
    color_discrete_sequence=["#636EFA"]
)
fig_dist.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")

# Salary by city
st.subheader("Salary by City")
city_salary = salary_jobs.groupby("location_display").agg(
    job_count=("job_id", "count"),
    avg_min=("salary_min", "mean"),
    avg_max=("salary_max", "mean"),
    median_mid=("salary_mid", "median")
).reset_index()

# Only show cities with at least 3 jobs for meaningful comparison
city_salary = city_salary[city_salary["job_count"] >= 3].sort_values("median_mid", ascending=False).head(10)

if len(city_salary) > 0:
    fig_city = go.Figure()
    fig_city.add_trace(go.Bar(
        name="Avg Min Salary",
        y=city_salary["location_display"],
        x=city_salary["avg_min"],
        orientation="h",
        marker_color="#636EFA",
        text=[f"£{int(v):,}" for v in city_salary["avg_min"]],
        textposition="inside"
    ))
    fig_city.add_trace(go.Bar(
        name="Avg Max Salary",
        y=city_salary["location_display"],
        x=city_salary["avg_max"] - city_salary["avg_min"],
        orientation="h",
        marker_color="#00CC96",
        text=[f"£{int(v):,}" for v in city_salary["avg_max"]],
        textposition="inside",
        base=city_salary["avg_min"]
    ))
    fig_city.update_layout(
        barmode="stack",
        title="Average Salary Range by City (min 3 jobs)",
        yaxis=dict(autorange="reversed"),
        height=450,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_city, use_container_width=True)
else:
    st.info("Not enough salary data per city for comparison.")

st.markdown("---")

# Salary by skill
st.subheader("Salary Premium by Skill")
st.markdown("Does knowing a specific skill correlate with higher salaries?")

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
        color_continuous_scale="blues",
        title="Median Salary by Skill (min 2 jobs with salary data)"
    )
    fig_skill_sal.update_traces(textposition="outside")
    fig_skill_sal.update_layout(
        showlegend=False, coloraxis_showscale=False,
        height=450, margin=dict(l=0, r=0, t=40, b=0),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_skill_sal, use_container_width=True)

    # Table view
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

st.markdown("---")
st.markdown(
    f"**Note:** Only {len(salary_jobs)} of {len(jobs)} jobs ({round(len(salary_jobs)/len(jobs)*100,1)}%) "
    f"include salary information. Results should be interpreted with this in mind."
)