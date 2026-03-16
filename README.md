# UK Job Market Intelligence Dashboard

A real-time intelligence dashboard that tracks skill demand, salary trends, and geographic hiring patterns across UK data analyst and business analyst job postings.

**[View Live Dashboard](https://job-market-dashboard-duikwthe3lryalzbkxvkjv.streamlit.app)**

## What It Does

- Collects 500+ live job postings from the Adzuna API across multiple search terms
- Extracts 40+ technical and soft skills from job titles and descriptions using regex pattern matching
- Analyses which skills employers demand most, how salaries vary by city and skill, and where hiring is concentrated
- Presents everything through an interactive 3-page Streamlit dashboard

## Key Findings

- **Excel, Power BI, and SQL** appear among the most frequently requested skills in UK data analyst job postings
- **London** dominates hiring volume, followed by Manchester, Belfast, and Birmingham
- Cloud skills (Azure, AWS) appear in a growing number of listings, signalling a shift toward cloud-based analytics
- Specific percentages and salary breakdowns are available in the live dashboard

## Dashboard Pages

**Home** — Headline metrics, top 15 skills ranked by frequency, job volume by city, and a skills category treemap.

**Skill Demand** — Deep dive into individual skills with city breakdowns and salary comparisons. Multi-select comparison to overlay skills side by side.

**Salary Insights** — Salary distribution histogram, city-by-city salary ranges, and salary premiums associated with specific skills.

## Tech Stack

| Component | Technology |
|---|---|
| Data Collection | Python, Adzuna API |
| Skill Extraction | Python, Regex |
| Database | SQL (SQLite) |
| Analysis | pandas |
| Visualisation | Plotly |
| Dashboard | Streamlit |
| Deployment | Streamlit Community Cloud |

## Architecture

```
Adzuna API
    ↓
Python Data Collection (requests)
    ↓
SQLite Database
    ↓
Skill Extraction (Regex)
    ↓
pandas Analysis
    ↓
Streamlit + Plotly Dashboard
    ↓
Streamlit Community Cloud (Live Deployment)
```

## How It Works

The data pipeline runs in three steps:

1. **collect_jobs.py** calls the Adzuna API with 11 skill-targeted search terms, paginates through results, and stores unique job postings in a SQLite database
2. **extract_skills.py** loads a configurable skills dictionary (JSON) and scans each job's title and description using regex patterns, logging matches to a separate table
3. The Streamlit dashboard reads directly from SQLite and generates all charts and metrics on the fly using pandas and Plotly

The full pipeline can be re-run with a single command:
```bash
python3 scripts/run_pipeline.py
```

## Run Locally

```bash
# Clone the repo
git clone https://github.com/Munib123456/job-market-dashboard.git
cd job-market-dashboard

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Re-collect fresh data — requires Adzuna API key
# Add your credentials to config/settings.py first
python3 scripts/run_pipeline.py

# Launch the dashboard
streamlit run dashboard/Home.py
```

## Project Structure

```
job-market-dashboard/
    config/
        skills_config.json          # Skill keywords and regex patterns
    scripts/
        collect_jobs.py             # Adzuna API data collection
        extract_skills.py           # Skill extraction from job descriptions
        run_pipeline.py             # Runs full pipeline in sequence
    dashboard/
        Home.py                     # Overview page
        pages/
            1_Skill_Demand.py       # Skill analysis page
            2_Salary_Insights.py    # Salary analysis page
    data/
        jobs.db                     # SQLite database
    requirements.txt
    .streamlit/config.toml          # Streamlit theme config
```

## Methodology Notes

- Job descriptions from Adzuna are capped at 500 characters, so skill extraction also scans job titles to improve coverage
- 34% of collected jobs have at least one identifiable technical skill — the remainder are generic recruitment ads without specific tool mentions
- Salary data is available for approximately 40-60% of listings, which is typical for UK job boards
- Skills are matched using case-insensitive regex with word boundary markers to minimise false positives (e.g. "R" won't match "Regular")

## Built By

**Munib Ahmed** — Final-year Computer Science student at Northumbria University, Newcastle.

[LinkedIn](https://www.linkedin.com/in/munib-ahmed-53a568294) | [Portfolio](https://munibsweb.netlify.app/)