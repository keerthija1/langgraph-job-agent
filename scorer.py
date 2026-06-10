import os
import json
import anthropic
import logging

logger = logging.getLogger(__name__)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
RESUME = open(os.path.join(os.path.dirname(__file__), "../resume.txt")).read()

def score_jobs(state: dict) -> dict:
    logger.info("Agent 2: Scoring jobs...")
    jobs = state.get("jobs", [])
    if not jobs:
        return {"scored_jobs": [], "top_jobs": [], "error": "No jobs found."}
    jobs_text = "\n\n".join([
        f"Job {i+1}:\nTitle: {j['title']}\nCompany: {j['company']}\nLocation: {j['location']}\nDescription: {j['description']}"
        for i, j in enumerate(jobs)
    ])
    prompt = f"""You are a career advisor evaluating job listings for a candidate.

CANDIDATE RESUME:
{RESUME}

JOB LISTINGS:
{jobs_text}

Score each job from 1-10 based on skills match, experience fit, AI relevance, and visa sponsorship likelihood.

Return ONLY a JSON array, no explanation:
[
  {{"job_index": 1, "score": 8, "reason": "Strong match"}},
  {{"job_index": 2, "score": 5, "reason": "Partial match"}}
]"""
    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    scores = json.loads(text)
    scored_jobs = []
    for s in scores:
        idx = s["job_index"] - 1
        if 0 <= idx < len(jobs):
            job = jobs[idx].copy()
            job["score"] = s["score"]
            job["score_reason"] = s["reason"]
            scored_jobs.append(job)
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    top_jobs = [j for j in scored_jobs if j["score"] >= 5][:3]
    logger.info(f"Agent 2: {len(top_jobs)} jobs scored 6+.")
    return {"scored_jobs": scored_jobs, "top_jobs": top_jobs}

def should_continue(state: dict) -> str:
    if not state.get("top_jobs"):
        return "deliver"
    return "tailor"