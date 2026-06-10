import os
import json
import anthropic
import logging

logger = logging.getLogger(__name__)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

RESUME = open(os.path.join(os.path.dirname(__file__), "../resume.txt")).read()

def score_jobs(state: dict) -> dict:
    """Agent 2 — Score each job against Keerthi's profile using Claude."""
    logger.info("Agent 2: Scoring jobs...")

    jobs = state.get("jobs", [])
    if not jobs:
        return {"scored_jobs": [], "top_jobs": [], "error": "No jobs found to score."}

    jobs_text = "\n\n".join([
        f"Job {i+1}:\nTitle: {j['title']}\nCompany: {j['company']}\nLocation: {j['location']}\nRemote: {j['is_remote']}\nDescription: {j['description']}"
        for i, j in enumerate(jobs)
    ])

    prompt = f"""You are a career advisor evaluating job listings for a candidate.

CANDIDATE RESUME:
{RESUME}

JOB LISTINGS:
{jobs_text}

Score each job from 1-10 based on:
- Skills match (does the job require skills the candidate has?)
- Experience level fit (is the candidate qualified?)
- Relevance to AI engineering transition
- Visa sponsorship likelihood (prefer companies known to sponsor H1B)

Return ONLY a JSON array like this, no explanation:
[
  {{"job_index": 1, "score": 8, "reason": "Strong match - requires Python and Claude API experience"}},
  {{"job_index": 2, "score": 5, "reason": "Partial match - requires ML experience not on resume"}}
]"""

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
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
    top_jobs = [j for j in scored_jobs if j["score"] >= 6][:3]

    logger.info(f"Agent 2: {len(top_jobs)} jobs scored 6+ out of {len(scored_jobs)}.")
    return {"scored_jobs": scored_jobs, "top_jobs": top_jobs}


def should_continue(state: dict) -> str:
    """Conditional edge — if no good jobs found, skip to delivery."""
    if not state.get("top_jobs"):
        logger.info("No jobs scored 6+. Skipping tailor.")
        return "deliver"
    return "tailor"