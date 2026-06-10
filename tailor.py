import os
import anthropic
import logging

logger = logging.getLogger(__name__)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

RESUME = open(os.path.join(os.path.dirname(__file__), "../resume.txt")).read()

def tailor_resume(state: dict) -> dict:
    """Agent 3 — Tailor resume bullets and write cover letter for each top job."""
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

Your tasks:
1. Rewrite the SUMMARY section to match this specific job — use keywords from the job description
2. Suggest 2-3 bullet point rewrites for the Experience section that better match this job
3. Write a short 3-paragraph cover letter (under 150 words total)

Format your response EXACTLY like this:

TAILORED SUMMARY:
[rewritten summary here]

SUGGESTED BULLET REWRITES:
• [rewritten bullet 1]
• [rewritten bullet 2]
• [rewritten bullet 3]

COVER LETTER:
[cover letter here]"""

        response = claude.messages.create(
            model="claude-opus-4-5",
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )

        tailored.append({
            "job": job,
            "tailored_content": response.content[0].text.strip(),
        })
        logger.info(f"Agent 3: Tailored resume for {job['title']} at {job['company']}")

    return {"tailored": tailored}
