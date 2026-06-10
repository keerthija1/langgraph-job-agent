import os
import requests
import logging

logger = logging.getLogger(__name__)

def search_jobs(state: dict) -> dict:
    logger.info("Agent 1: Searching for jobs...")
    all_jobs = []
    headers = {
        "x-rapidapi-host": os.environ["RAPIDAPI_HOST"],
        "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
    }

    try:
        response = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params={
                "query": "AI Engineer United States",
                "num_pages": "1",
            },
            timeout=15,
        )
        logger.info(f"API status code: {response.status_code}")
        data = response.json()
        logger.info(f"API response keys: {list(data.keys())}")
        logger.info(f"Jobs in response: {len(data.get('data', []))}")
        if data.get("message"):
            logger.info(f"API message: {data.get('message')}")
        if data.get("status"):
            logger.info(f"API status: {data.get('status')}")

        for job in data.get("data", [])[:3]:
            all_jobs.append({
                "title": job.get("job_title", ""),
                "company": job.get("employer_name", ""),
                "location": job.get("job_city", "") + ", " + job.get("job_state", ""),
                "description": job.get("job_description", "")[:800],
                "url": job.get("job_apply_link", ""),
                "is_remote": job.get("job_is_remote", False),
            })
    except Exception as e:
        logger.error(f"Search error: {e}")

    logger.info(f"Agent 1: Found {len(all_jobs)} jobs.")
    return {"jobs": all_jobs, "error": None}