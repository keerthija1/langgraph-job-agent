import os
import requests
import logging
import smtplib
import tempfile
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
MAX_MSG_LENGTH = 4000

RESUME_DATA = {
    "name": "Keerthi Jakkireddy",
    "contact": "Ankeny, Iowa, US  |  jakkireddykeerthi@gmail.com  |  3302683501",
    "experience": [
        {
            "title": "IT Field Support Specialist — Cargill",
            "date": "January 2025 – Present  |  Ankeny, Iowa, US",
            "bullets": [
                "Monitor and resolve 50+ IT support tickets per month via ServiceNow, handling hardware, software, and access issues.",
                "Managed end-to-end device lifecycle for 50+ laptops — tracked warranty expirations, coordinated replacements, performed setups, and executed disk wipes on returned devices.",
                "Proposed and designed an AI-powered automation plan to eliminate manual warranty tracking using Power Automate and ServiceNow, targeting reduction of 10+ hours of manual effort per month.",
                "Provide admin rights management and user account administration across the organization.",
                "Perform device imaging, system setup, and hardware troubleshooting across the organization.",
            ]
        },
        {
            "title": "SAP Basis Consultant — DXC Technology",
            "date": "June 2021 – July 2022  |  India",
            "bullets": [
                "Managed SAP systems for client Syngenta, ensuring smooth operation and system availability.",
                "Handled transport requests across SAP environments as per client requirements.",
                "Performed daily health checks, system monitoring, and issue resolution to maintain uptime.",
                "Configured system downtimes and maintenance windows for planned activities.",
                "Resolved user incidents, system-generated alerts, and ABAP dumps.",
                "Collaborated directly with clients to address queries and deliver timely solutions.",
            ]
        }
    ],
    "projects": [
        ("Gmail Triage Agent", [
            "Built an autonomous agent that reads 100+ incoming emails, classifies them by priority, and reduces them to ~20 actionable items — eliminating manual inbox sorting entirely.",
            "Deployed on Google Cloud Run with secrets managed via GCP Secret Manager — runs 24/7 with no manual trigger.",
        ]),
        ("AI News Digest Agent", [
            "Autonomous agent that searches and aggregates AI news from multiple websites daily, filters the most relevant stories, and delivers a concise digest to Telegram every evening.",
            "Fully deployed on Railway with scheduled execution — saves 30+ minutes of manual research daily with zero human intervention.",
        ]),
        ("LangGraph Job Search & Resume Tailor Agent", [
            "Built a 4-agent LangGraph pipeline — job searcher, scorer, resume tailor, and Telegram delivery — that collaborates autonomously to automate the entire job application workflow.",
            "Agent searches AI engineering roles daily, scores each listing against candidate profile, tailors resume bullets and generates a cover letter for top 3 matches.",
        ]),
        ("LinkedIn Blog Agent", [
            "Built an end-to-end content pipeline agent that searches trending AI topics, writes structured LinkedIn posts using Claude, and delivers drafts to Telegram for review before publishing.",
            "Generates 2 posts per week (8+ per month) automatically — runs every Tuesday and Thursday at 8 AM CST on Railway.",
        ]),
    ],
    "education": "Master of Science in Computer Science — Youngstown State University  |  August 2022 – May 2024",
    "skills": [
        ("AI & Agents", "Anthropic Claude API, Tavily API, LangGraph, LangChain, Prompt Engineering, APScheduler, Multi-Tool Orchestration, Human-in-the-Loop Design"),
        ("Languages", "Python, Java, SQL, Bash"),
        ("Cloud & DevOps", "Google Cloud Run, Railway, GCP Secret Manager, GitHub, CI/CD"),
        ("APIs & Tools", "Gmail API, Telegram Bot API, Flask, ServiceNow, Jira, Splunk, Power Automate, SAP Basis"),
        ("Databases & Search", "Vector Search, Real-Time Web Search"),
        ("Other", "Asset Management, Device Imaging, System Troubleshooting, IT Help Desk, Autonomous Agent Design"),
    ]
}


def parse_tailored_content(content: str) -> dict:
    sections = {"summary": "", "bullets": [], "cover_letter": ""}
    current = None
    for line in content.split("\n"):
        line = line.strip()
        if "TAILORED SUMMARY:" in line:
            current = "summary"
        elif "SUGGESTED BULLET REWRITES:" in line:
            current = "bullets"
        elif "COVER LETTER:" in line:
            current = "cover_letter"
        elif current == "summary" and line:
            sections["summary"] += line + " "
        elif current == "bullets" and line and line[0] in "•-*":
            sections["bullets"].append(line.lstrip("•-* ").strip())
        elif current == "cover_letter" and line:
            sections["cover_letter"] += line + "\n"
    return sections


def generate_resume_pdf(job: dict, tailored: dict, output_path: str):
    BLACK = colors.HexColor("#000000")
    DARK = colors.HexColor("#222222")
    GRAY = colors.HexColor("#444444")
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.65*inch, rightMargin=0.65*inch)
    name_style    = ParagraphStyle("name",    fontSize=16, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_CENTER, spaceAfter=2)
    contact_style = ParagraphStyle("contact", fontSize=9,  fontName="Helvetica",      textColor=DARK,  alignment=TA_CENTER, spaceAfter=4)
    section_style = ParagraphStyle("section", fontSize=10, fontName="Helvetica-Bold", textColor=BLACK, spaceBefore=8, spaceAfter=2)
    job_co_style  = ParagraphStyle("jobco",   fontSize=9,  fontName="Helvetica-Bold", textColor=BLACK, spaceAfter=0)
    job_dt_style  = ParagraphStyle("jobdt",   fontSize=9,  fontName="Helvetica",      textColor=GRAY,  spaceAfter=2)
    bullet_style  = ParagraphStyle("bullet",  fontSize=9,  fontName="Helvetica",      textColor=DARK,  leftIndent=14, spaceAfter=2, leading=13)
    normal_style  = ParagraphStyle("normal",  fontSize=9,  fontName="Helvetica",      textColor=DARK,  spaceAfter=2, leading=13)
    proj_style    = ParagraphStyle("proj",    fontSize=9,  fontName="Helvetica-Bold", textColor=BLACK, spaceAfter=1, spaceBefore=4)

    def sec(title):
        return [Paragraph(title.upper(), section_style),
                HRFlowable(width="100%", thickness=0.75, color=BLACK, spaceAfter=4)]
    def bul(text):
        return Paragraph(f"• {text}", bullet_style)

    story = []
    story.append(Paragraph(RESUME_DATA["name"], name_style))
    story.append(Paragraph(RESUME_DATA["contact"], contact_style))
    story += sec("Summary")
    story.append(Paragraph(tailored.get("summary", "").strip(), normal_style))
    story += sec("Experience")
    tailored_bullets = tailored.get("bullets", [])
    for i, exp in enumerate(RESUME_DATA["experience"]):
        story.append(Paragraph(exp["title"], job_co_style))
        story.append(Paragraph(exp["date"], job_dt_style))
        bullets = tailored_bullets if i == 0 and tailored_bullets else exp["bullets"]
        for b in bullets:
            story.append(bul(b))
        story.append(Spacer(1, 4))
    story += sec("Projects")
    for title, bullets in RESUME_DATA["projects"]:
        story.append(Paragraph(title, proj_style))
        for b in bullets:
            story.append(bul(b))
    story += sec("Education")
    story.append(Paragraph(RESUME_DATA["education"], normal_style))
    story += sec("Skills")
    for cat, items in RESUME_DATA["skills"]:
        story.append(Paragraph(f"<b>{cat}:</b> {items}", normal_style))
    doc.build(story)


def generate_cover_letter_pdf(job: dict, tailored: dict, output_path: str):
    BLACK = colors.HexColor("#000000")
    DARK = colors.HexColor("#222222")
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)
    name_style    = ParagraphStyle("name",    fontSize=14, fontName="Helvetica-Bold", textColor=BLACK, spaceAfter=2)
    contact_style = ParagraphStyle("contact", fontSize=9,  fontName="Helvetica",      textColor=DARK,  spaceAfter=16)
    normal_style  = ParagraphStyle("normal",  fontSize=10, fontName="Helvetica",      textColor=DARK,  spaceAfter=10, leading=15)
    story = []
    story.append(Paragraph(RESUME_DATA["name"], name_style))
    story.append(Paragraph(RESUME_DATA["contact"], contact_style))
    story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), normal_style))
    story.append(Spacer(1, 12))
    for para in tailored.get("cover_letter", "").strip().split("\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), normal_style))
    doc.build(story)


def send_email(subject: str, body: str, attachments: list):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    for filepath, filename in attachments:
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())


def send_telegram(text: str):
    chunks = [text[i:i+MAX_MSG_LENGTH] for i in range(0, len(text), MAX_MSG_LENGTH)]
    for chunk in chunks:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"})


def deliver(state: dict) -> dict:
    logger.info("Agent 4: Delivering to Telegram and Email...")
    date_str = datetime.now().strftime("%A, %b %d %Y")
    tailored = state.get("tailored", [])
    top_jobs = state.get("top_jobs", [])
    error = state.get("error")

    if error or not top_jobs:
        send_telegram(
            f"🤖 *Job Search Agent — {date_str}*\n\n"
            f"No strong matches found today.\n"
            f"Total reviewed: {len(state.get('scored_jobs', []))}\n\n"
            f"Will check again tomorrow! 💪"
        )
        return {"message": "No matches found"}

    summary = (f"🤖 *Job Search Agent — {date_str}*\n\n"
               f"✅ Found *{len(top_jobs)} match(es)*\n"
               f"📧 Tailored resume + cover letter sent to your email!\n\n"
               f"━━━━━━━━━━━━━━━━━━━━\n")

    for i, item in enumerate(tailored):
        job = item["job"]
        remote = "🌐 Remote" if job.get("is_remote") else f"📍 {job['location']}"
        msg = (f"\n🎯 *Match {i+1} — Score {job['score']}/10*\n"
               f"*{job['title']}*\n"
               f"🏢 {job['company']}  |  {remote}\n"
               f"🔗 [Apply Here]({job['url']})\n"
               f"💡 _{job['score_reason']}_\n")
        send_telegram(summary + msg if i == 0 else msg)

        try:
            parsed = parse_tailored_content(item["tailored_content"])
            company = "".join(c for c in job["company"] if c.isalnum() or c == "_")
            with tempfile.TemporaryDirectory() as tmpdir:
                resume_path = f"{tmpdir}/Keerthi_Resume_{company}.pdf"
                cover_path  = f"{tmpdir}/Keerthi_CoverLetter_{company}.pdf"
                generate_resume_pdf(job, parsed, resume_path)
                generate_cover_letter_pdf(job, parsed, cover_path)
                send_email(
                    subject=f"Job Match: {job['title']} at {job['company']} — {date_str}",
                    body=(f"Hi Keerthi,\n\nYour Job Search Agent found a match!\n\n"
                          f"Role: {job['title']}\nCompany: {job['company']}\n"
                          f"Location: {remote}\nScore: {job['score']}/10\n"
                          f"Apply: {job['url']}\n\n"
                          f"Attached: tailored resume and cover letter PDFs.\n\nGood luck!"),
                    attachments=[
                        (resume_path, f"Keerthi_Resume_{company}.pdf"),
                        (cover_path,  f"Keerthi_CoverLetter_{company}.pdf"),
                    ]
                )
            logger.info(f"Agent 4: Email sent for {job['title']} at {job['company']}")
        except Exception as e:
            logger.error(f"Email/PDF error: {e}")

    logger.info("Agent 4: Delivered successfully.")
    return {"message": "Delivered successfully"}