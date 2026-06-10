import os
import requests
import logging

logger = logging.getLogger(__name__)

def search_jobs(state: dict) -> dict:
    """Agent 1 — Search for AI engineering jobs using JSearch API."""
    logger.info("Agent 1: Searching for jobs...")

    queries = [
        "AI Engineer",
        "AI Automation Engineer",
        "LLM Engineer",
        "Prompt Engineer",
        "AI Integration Engineer",
    ]

    all_jobs = []
    headers = {
        "x-rapidapi-host": os.environ["RAPIDAPI_HOST"],
        "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
    }

    for query in queries:
        try:
            response = requests.get(
                "https://jsearch.p.rapidapi.com/search",
                headers=headers,
                params={
                    "query": f"{query} jobs in United States",
                    "num_pages": "1",
                    "date_posted": "today",
                },
                timeout=15,
            )
            data = response.json()
            jobs = data.get("data", [])
            for job in jobs[:3]:
                all_jobs.append({
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "location": job.get("job_city", "") + ", " + job.get("job_state", ""),
                    "description": job.get("job_description", "")[:800],
                    "url": job.get("job_apply_link", ""),
                    "employment_type": job.get("job_employment_type", ""),
                    "is_remote": job.get("job_is_remote", False),
                })
        except Exception as e:
            logger.error(f"Search error for query '{query}': {e}")

    # Deduplicate by URL
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique_jobs.append(job)

    logger.info(f"Agent 1: Found {len(unique_jobs)} unique jobs.")
    return {"jobs": unique_jobs[:15], "error": None}
