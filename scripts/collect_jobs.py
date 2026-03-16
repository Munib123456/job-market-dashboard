import requests
import sqlite3
import sys
import os
from datetime import datetime

# Add project root to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import ADZUNA_APP_ID, ADZUNA_APP_KEY, DB_PATH, SEARCH_TERMS, MAX_PAGES, RESULTS_PER_PAGE, MAX_DAYS_OLD


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT,
            location_display TEXT,
            location_area TEXT,
            salary_min REAL,
            salary_max REAL,
            description TEXT,
            created_date TEXT,
            collected_date TEXT,
            source_url TEXT,
            search_term TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            skill_category TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        )
    """)
    conn.commit()
    return conn


def fetch_jobs(search_term, page):
    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": search_term,
        "max_days_old": MAX_DAYS_OLD,
        "content-type": "application/json"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"  ERROR: API returned status {response.status_code} for '{search_term}' page {page}")
        print(f"  Response: {response.text[:200]}")
        return []
    data = response.json()
    return data.get("results", [])


def parse_job(job, search_term):
    location = job.get("location", {})
    area_list = location.get("area", [])
    area_string = " > ".join(area_list) if area_list else ""
    return (
        str(job.get("id", "")),
        job.get("title", ""),
        job.get("company", {}).get("display_name", ""),
        location.get("display_name", ""),
        area_string,
        job.get("salary_min"),
        job.get("salary_max"),
        job.get("description", ""),
        job.get("created", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        job.get("redirect_url", ""),
        search_term
    )


def collect_all_jobs():
    conn = create_database()
    cursor = conn.cursor()

    total_found = 0
    new_added = 0
    duplicates = 0

    for term in SEARCH_TERMS:
        print(f"\nSearching for: '{term}'")
        for page in range(1, MAX_PAGES + 1):
            print(f"  Page {page}/{MAX_PAGES}...", end=" ")
            jobs = fetch_jobs(term, page)
            if not jobs:
                print("No results.")
                break
            print(f"{len(jobs)} jobs found.")
            total_found += len(jobs)
            for job in jobs:
                parsed = parse_job(job, term)
                try:
                    cursor.execute("""
                        INSERT INTO jobs (job_id, title, company, location_display, location_area,
                                         salary_min, salary_max, description, created_date,
                                         collected_date, source_url, search_term)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, parsed)
                    new_added += 1
                except sqlite3.IntegrityError:
                    duplicates += 1

    conn.commit()
    conn.close()

    print("\n" + "=" * 40)
    print("COLLECTION COMPLETE")
    print("=" * 40)
    print(f"Total jobs found:    {total_found}")
    print(f"New jobs added:      {new_added}")
    print(f"Duplicates skipped:  {duplicates}")
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    collect_all_jobs()