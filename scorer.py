import os
import json
import anthropic
import logging

logger = logging.getLogger(__name__)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
RESUME = """Keerthi Jakkireddy
Ankeny, Iowa, US | jakkireddykeerthi@gmail.com | 3302683501

SUMMARY
AI Automation Engineer with hands-on experience building and deploying autonomous AI agents that eliminate manual work at scale. Built multi-agent pipelines using LangGraph, triage 100+ emails down to 20 actionable items, deliver daily AI news digests, and automate LinkedIn content — all deployed to production on GCP and Railway. Background in IT support and SAP Basis consulting, with a Master's in Computer Science. Focused on building AI systems that solve real operational problems with zero human trigger.

EXPERIENCE
IT Field Support Specialist — Cargill | January 2025 – Present | Ankeny, Iowa, US
- Monitor and resolve 50+ IT support tickets per month via ServiceNow, handling hardware, software, and access issues.
- Managed end-to-end device lifecycle for 50+ laptops — tracked warranty expirations, coordinated replacements, performed setups, and executed disk wipes on returned devices.
- Proposed and designed an AI-powered automation plan to eliminate manual warranty tracking using Power Automate and ServiceNow, targeting reduction of 10+ hours of manual effort per month.
- Provide admin rights management and user account administration across the organization.
- Perform device imaging, system setup, and hardware troubleshooting across the organization.

SAP Basis Consultant — DXC Technology | June 2021 – July 2022 | India
- Managed SAP systems for client Syngenta, ensuring smooth operation and system availability.
- Handled transport requests across SAP environments as per client requirements.
- Performed daily health checks, system monitoring, and issue resolution to maintain uptime.
- Configured system downtimes and maintenance windows for planned activities.
- Resolved user incidents, system-generated alerts, and ABAP dumps.
- Collaborated directly with clients to address queries and deliver timely solutions.

PROJECTS
Gmail Triage Agent
- Built an autonomous agent that reads 100+ incoming emails, classifies them by priority, and reduces them to ~20 actionable items — eliminating manual inbox sorting entirely.
- Deployed on Google Cloud Run with secrets managed via GCP Secret Manager — runs 24/7 with no manual trigger.

AI News Digest Agent
- Autonomous agent that searches and aggregates AI news from multiple websites daily, filters the most relevant stories, and delivers a concise digest to Telegram every evening.
- Fully deployed on Railway with scheduled execution — saves 30+ minutes of manual research daily with zero human intervention.

LangGraph Job Search & Resume Tailor Agent
- Built a 4-agent LangGraph pipeline — job searcher, scorer, resume tailor, and Telegram delivery — that collaborates autonomously to automate the entire job application workflow.
- Agent searches AI engineering roles daily, scores each listing against candidate profile, tailors resume bullets and generates a cover letter for top 3 matches, and delivers everything to Telegram every weekday morning at 7 AM CST.

LinkedIn Blog Agent
- Built an end-to-end content pipeline agent that searches trending AI topics, writes structured LinkedIn posts using Claude, and delivers drafts to Telegram for review before publishing.
- Generates 2 posts per week (8+ per month) automatically — runs every Tuesday and Thursday at 8 AM CST on Railway with human-in-the-loop approval before publishing.

EDUCATION
Master of Science in Computer Science — Youngstown State University | August 2022 – May 2024

SKILLS
AI & Agents: Anthropic Claude API, Tavily API, LangGraph, LangChain, Prompt Engineering, APScheduler, Multi-Tool Orchestration, Human-in-the-Loop Design
Languages: Python, Java, SQL, Bash
Cloud & DevOps: Google Cloud Run, Railway, GCP Secret Manager, GitHub, CI/CD
APIs & Tools: Gmail API, Telegram Bot API, Flask, ServiceNow, Jira, Splunk, Power Automate, SAP Basis
Databases & Search: Vector Search, Real-Time Web Search
Other: Asset Management, Device Imaging, System Troubleshooting, IT Help Desk, Autonomous Agent Design"""

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
Do NOT penalize for visa sponsorship — ignore that factor entirely.

Return ONLY a JSON array, no explanation:
[
  {{"job_index": 1, "score": 8, "reason": "Strong match - requires Python and Claude API experience"}},
  {{"job_index": 2, "score": 5, "reason": "Partial match - requires ML experience not on resume"}}
]"""
]