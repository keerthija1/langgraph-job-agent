import os
import logging
from langgraph.graph import StateGraph, END
from apscheduler.schedulers.blocking import BlockingScheduler
from state import JobState
from nodes.searcher import search_jobs
from nodes.scorer import score_jobs, should_continue
from nodes.tailor import tailor_resume
from nodes.delivery import deliver

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def build_graph():
    """Build the LangGraph multi-agent pipeline."""
    graph = StateGraph(JobState)

    # Add nodes (agents)
    graph.add_node("search",  search_jobs)
    graph.add_node("score",   score_jobs)
    graph.add_node("tailor",  tailor_resume)
    graph.add_node("deliver", deliver)

    # Define flow
    graph.set_entry_point("search")
    graph.add_edge("search", "score")

    # Conditional edge — if no good jobs skip tailoring
    graph.add_conditional_edges(
        "score",
        should_continue,
        {
            "tailor":  "tailor",
            "deliver": "deliver",
        }
    )

    graph.add_edge("tailor",  "deliver")
    graph.add_edge("deliver", END)

    return graph.compile()


def run_agent():
    """Run the full pipeline."""
    logger.info("=== LangGraph Job Search Agent started ===")
    try:
        app = build_graph()
        result = app.invoke({
            "jobs": [],
            "scored_jobs": [],
            "top_jobs": [],
            "tailored": [],
            "message": "",
            "error": None,
        })
        logger.info(f"=== Agent complete: {result.get('message')} ===")
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        raise


def main():
    # Run once immediately on startup
    run_agent()

    # Schedule Mon–Fri at 7:00 AM CST
    scheduler = BlockingScheduler(timezone="America/Chicago")
    scheduler.add_job(run_agent, "cron", day_of_week="mon-fri", hour=7, minute=0)
    logger.info("Scheduler started — running Mon–Fri at 7:00 AM CST.")
    scheduler.start()


if __name__ == "__main__":
    main()
