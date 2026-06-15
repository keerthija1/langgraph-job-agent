import os
import requests
import logging
import time

logger = logging.getLogger(__name__)

def search_jobs(state: dict) -> dict:
    logger.info("Agent 1: Searching for jobs...")
    all_jobs = []
    headers = {
        "x-rapidapi-host": os.environ["RAPIDAPI_HOST"],
        "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
    }
    queries = ["AI Engineer", "AI Automation Engineer", "LLM Engineer", "Prompt Engineer"]
    for query in queries:
        try:
            for attempt in range(3):
                try:
                    response = requests.get(
                        "https://jsearch.p.rapidapi.com/search",
                        headers=headers,
                        params={"query": f"{query} United States", "num_pages": "3", "date_posted": "3days"},
                        timeout=30,
                    )
                    break
                except requests.exceptions.Timeout:
                    logger.warning(f"Timeout on attempt {attempt+1} for '{query}', retrying...")
                    time.sleep(5)
            data = response.json()
            for job in data.get("data", [])[:3]:
                all_jobs.append({
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "location": f"{job.get('job_city') or ''}, {job.get('job_state') or ''}".strip(", "), 
                    "description": job.get("job_description", "")[:4000],
                    "url": job.get("job_apply_link", ""),
                    "is_remote": job.get("job_is_remote", False),
                })
        except Exception as e:
            logger.error(f"Search error for '{query}': {e}")

    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique_jobs.append(job)

    logger.info(f"Agent 1: Found {len(unique_jobs)} unique jobs.")
    return {"jobs": unique_jobs[:15], "error": None}