import os
import anthropic
import logging

logger = logging.getLogger(__name__)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
RESUME = open(os.path.join(os.path.dirname(__file__), "../resume.txt")).read()

def tailor_resume(state: dict) -> dict:
    logger.info("Agent 3: Tailoring resumes...")
    top_jobs = state.get("top_jobs", [])
    tailored = []
    for job in top_jobs:
        prompt = f"""You are an expert resume writer tailoring a resume for a specific job.

CANDIDATE RESUME:
{RESUME}

TARGET JOB:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}

Tasks:
1. Rewrite the SUMMARY to match this job
2. Suggest 2-3 bullet rewrites for Experience
3. Write a short cover letter under 150 words

Format EXACTLY like this:

TAILORED SUMMARY:
[rewritten summary]

SUGGESTED BULLET REWRITES:
- [bullet 1]
- [bullet 2]
- [bullet 3]

COVER LETTER:
[cover letter]"""
        response = claude.messages.create(
            model="claude-opus-4-5",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        tailored.append({"job": job, "tailored_content": response.content[0].text.strip()})
        logger.info(f"Agent 3: Tailored for {job['title']} at {job['company']}")
    return {"tailored": tailored}