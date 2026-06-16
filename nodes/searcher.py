import os
import time
import requests
import logging

logger = logging.getLogger(__name__)

EXCLUDED_KEYWORDS = [
    "freelance", "contract-to-hire", "data annotation", "annotator",
    "labeler", "labelling", "part-time", "part time", "intern",
    "volunteer", "temporary", "gig"
]

def is_valid_job(job):
    text = (job["title"] + " " + job["description"]).lower()
    return not any(kw in text for kw in EXCLUDED_KEYWORDS)


def search_jobs(state: dict) -> dict:
    logger.info("Agent 1: Searching for jobs...")
    all_jobs = []

    headers = {
        "x-rapidapi-host": os.environ["RAPIDAPI_HOST"],
        "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
    }

    queries = [
        "AI Engineer",
        "Machine Learning Engineer",
        "LLM Engineer",
        "Prompt Engineer",
        "AI Developer",
        "Generative AI Engineer",
        "Python AI Engineer",
        "AI Agent Developer",
        "AI Automation Engineer",
        "AI Integration Engineer",
        "NLP Engineer",
        "AI Solutions Engineer",
        "AI Backend Engineer",
        "MLOps Engineer",
        "Conversational AI Engineer",
    ]

    for query in queries:
        for attempt in range(3):
            try:
                response = requests.get(
                    "https://jsearch.p.rapidapi.com/search",
                    headers=headers,
                    params={
                        "query": f"{query} United States",
                        "num_pages": "3",
                        "date_posted": "3days",
                    },
                    timeout=30,
                )
                data = response.json()
                for job in data.get("data", [])[:5]:
                    all_jobs.append({
                        "title": job.get("job_title", ""),
                        "company": job.get("employer_name", ""),
                        "location": f"{job.get('job_city') or ''}, {job.get('job_state') or ''}".strip(", "),
                        "description": job.get("job_description", "")[:3000],
                        "url": job.get("job_apply_link", ""),
                        "is_remote": job.get("job_is_remote", False),
                        "source": "JSearch",
                    })
                break
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt+1} for '{query}', retrying...")
                time.sleep(5)
            except Exception as e:
                logger.error(f"JSearch error for '{query}': {e}")
                break

    # Deduplicate and filter
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] and job["url"] not in seen and is_valid_job(job):
            seen.add(job["url"])
            unique_jobs.append(job)

    logger.info(f"Agent 1: Found {len(unique_jobs)} unique jobs.")
    return {"jobs": unique_jobs[:25], "error": None}