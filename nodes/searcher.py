import os
import time
import requests
import logging
from tavily import TavilyClient

logger = logging.getLogger(__name__)
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

EXCLUDED_KEYWORDS = [
    "freelance", "contract-to-hire", "data annotation", "annotator",
    "labeler", "labelling", "part-time", "part time", "intern",
    "volunteer", "temporary", "gig"
]

def is_valid_job(job):
    text = (job["title"] + " " + job["description"]).lower()
    return not any(kw in text for kw in EXCLUDED_KEYWORDS)


def search_jsearch(headers):
    """Search jobs via JSearch API."""
    all_jobs = []
    queries = [
        "AI Engineer",
        "Machine Learning Engineer",
        "LLM Engineer",
        "Prompt Engineer",
        "AI Developer",
        "Generative AI Engineer",
        "Python AI Engineer",
        "AI Agent Developer",
    ]
    for query in queries:
        for attempt in range(3):
            try:
                response = requests.get(
                    "https://jsearch.p.rapidapi.com/search",
                    headers=headers,
                    params={"query": f"{query} United States", "num_pages": "3", "date_posted": "3days"},
                    timeout=30,
                )
                data = response.json()
                for job in data.get("data", [])[:3]:
                    all_jobs.append({
                        "title": job.get("job_title", ""),
                        "company": job.get("employer_name", ""),
                        "location": f"{job.get('job_city') or ''}, {job.get('job_state') or ''}".strip(", "),
                        "description": job.get("job_description", "")[:3000],
                        "url": job.get("job_apply_link", ""),
                        "is_remote": job.get("job_is_remote", False),
                        "source": "JSearch"
                    })
                break
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt+1} for '{query}', retrying...")
                time.sleep(5)
            except Exception as e:
                logger.error(f"JSearch error for '{query}': {e}")
                break
    return all_jobs


def search_tavily_site(query, site):
    """Search jobs from a specific site via Tavily."""
    try:
        results = tavily.search(
            query=f"{query} full time OR contract jobs site:{site}",
            search_depth="basic",
            max_results=5,
        )
        jobs = []
        for r in results.get("results", []):
            jobs.append({
                "title": r.get("title", ""),
                "company": "",
                "location": "Remote / US",
                "description": r.get("content", "")[:3000],
                "url": r.get("url", ""),
                "is_remote": True,
                "source": site,
            })
        return jobs
    except Exception as e:
        logger.error(f"Tavily error for {site}: {e}")
        return []
    


def search_jobs(state: dict) -> dict:
    logger.info("Agent 1: Searching for jobs...")
    all_jobs = []

    # JSearch — pulls from LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google Jobs
    headers = {
        "x-rapidapi-host": os.environ["RAPIDAPI_HOST"],
        "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
    }
    all_jobs += search_jsearch(headers)

    # Tavily — AI-specific job boards
    tavily_queries = ["AI Engineer", "LLM Engineer"]
    tavily_sites = [
        "wellfound.com",
        "aijobs.net",
        "huggingface.co/jobs",
        "jobright.ai",
        "remoteai.jobs",
        "otta.com",
        "workatastartup.com",
        "ai-jobs.net",
        "builtin.com",
        "dice.com",
    ]
    for site in tavily_sites:
        for query in tavily_queries:
            all_jobs += search_tavily_site(query, site)

    # Deduplicate and filter
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] and job["url"] not in seen and is_valid_job(job):
            seen.add(job["url"])
            unique_jobs.append(job)

    logger.info(f"Agent 1: Found {len(unique_jobs)} unique jobs.")
    return {"jobs": unique_jobs[:20], "error": None}