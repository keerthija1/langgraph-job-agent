import os
import json
import anthropic
import logging

logger = logging.getLogger(__name__)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

try:
    RESUME = open(os.path.join(os.path.dirname(__file__), "../resume.txt")).read()
    logger.info(f"Resume loaded: {len(RESUME)} characters")
except Exception as e:
    logger.error(f"Failed to load resume: {e}")
    RESUME = ""

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

    prompt = f"""You are a career advisor evaluating job listings for a candidate transitioning into AI engineering.

CANDIDATE RESUME:
{RESUME}

JOB LISTINGS:
{jobs_text}

Score each job from 1-10 using these criteria:
- 8-10: Strong match — requires Python, AI/LLM tools, automation, or agent development. Candidate clearly qualifies.
- 6-7: Good match — partial overlap with candidate's skills, reasonable to apply.
- 4-5: Weak match — some transferable skills but significant gaps.
- 1-3: Poor match — very different domain or requires years of experience candidate lacks.

Be generous — if the candidate has 60%+ of the required skills, score it 6 or above.
Do NOT consider visa sponsorship in your scoring — ignore that factor entirely.

Return ONLY a JSON array, no explanation:
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
    logger.info(f"Scores from Claude: {scores}")

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