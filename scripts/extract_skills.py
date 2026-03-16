import sqlite3
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DB_PATH

SKILLS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "skills_config.json")


def load_skills():
    with open(SKILLS_CONFIG_PATH, "r") as f:
        return json.load(f)


def extract_skills():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear old skill extractions so we can re-run cleanly
    cursor.execute("DELETE FROM job_skills")

    # Load all jobs
    cursor.execute("SELECT job_id, title, description FROM jobs")
    jobs = cursor.fetchall()

    # Load skills config
    skills = load_skills()

    total_matches = 0
    skill_counts = {}

    for job_id, title, description in jobs:
        text = f"{title or ''} {description or ''}"
        if not text.strip():
            continue
        for category, skill_dict in skills.items():
            for skill_name, pattern in skill_dict.items():
                if re.search(pattern, text, re.IGNORECASE):
                    cursor.execute(
                        "INSERT INTO job_skills (job_id, skill_name, skill_category) VALUES (?, ?, ?)",
                        (job_id, skill_name, category)
                    )
                    total_matches += 1
                    skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1

    conn.commit()
    conn.close()

    # Print summary
    print(f"\nProcessed {len(jobs)} jobs.")
    print(f"Total skill matches: {total_matches}")
    print(f"\nTop 10 skills:")
    print("-" * 30)
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    for skill, count in sorted_skills[:10]:
        pct = round(count / len(jobs) * 100, 1)
        print(f"  {skill:<25} {count:>4} ({pct}%)")


if __name__ == "__main__":
    extract_skills()