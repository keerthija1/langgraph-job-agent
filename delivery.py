import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MAX_MSG_LENGTH = 4000

def send_message(text: str):
    """Send a message to Telegram, splitting if too long."""
    chunks = [text[i:i+MAX_MSG_LENGTH] for i in range(0, len(text), MAX_MSG_LENGTH)]
    for chunk in chunks:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown",
        })
        if response.status_code != 200:
            logger.error(f"Telegram error: {response.status_code} - {response.text}")


def deliver(state: dict) -> dict:
    """Agent 4 — Format and deliver results to Telegram."""
    logger.info("Agent 4: Delivering to Telegram...")

    date_str = datetime.now().strftime("%A, %b %d %Y")
    tailored = state.get("tailored", [])
    top_jobs = state.get("top_jobs", [])
    error = state.get("error")

    # Case: no good jobs found
    if error or not top_jobs:
        send_message(
            f"🤖 *Job Search Agent — {date_str}*\n\n"
            f"No strong job matches found today (score 6+).\n"
            f"Total jobs reviewed: {len(state.get('scored_jobs', []))}\n\n"
            f"Will check again tomorrow! 💪"
        )
        return {"message": "No matches found"}

    # Header summary
    summary = f"🤖 *Job Search Agent — {date_str}*\n\n"
    summary += f"✅ Found *{len(top_jobs)} strong matches* out of {len(state.get('scored_jobs', []))} jobs reviewed\n\n"
    summary += "━━━━━━━━━━━━━━━━━━━━\n"

    for i, item in enumerate(tailored):
        job = item["job"]
        content = item["tailored_content"]
        remote = "🌐 Remote" if job.get("is_remote") else f"📍 {job['location']}"

        msg = f"\n🎯 *Match {i+1} — Score {job['score']}/10*\n"
        msg += f"*{job['title']}*\n"
        msg += f"🏢 {job['company']}  |  {remote}\n"
        msg += f"🔗 [Apply Here]({job['url']})\n"
        msg += f"💡 _{job['score_reason']}_\n\n"
        msg += f"{content}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━"

        send_message(summary + msg if i == 0 else msg)

    logger.info("Agent 4: Delivered successfully.")
    return {"message": "Delivered successfully"}
