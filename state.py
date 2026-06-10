from typing import TypedDict, List, Optional

class JobState(TypedDict):
    jobs: List[dict]           # Raw jobs from JSearch API
    scored_jobs: List[dict]    # Jobs with scores from Claude
    top_jobs: List[dict]       # Top 3 jobs after filtering
    tailored: List[dict]       # Tailored resume + cover letter per job
    message: str               # Final Telegram message
    error: Optional[str]       # Error message if something fails
