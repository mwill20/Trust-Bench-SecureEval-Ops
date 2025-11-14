"""Entry point for the simplified Project 2 multi-agent system."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from multi_agent_system import (
    build_orchestrator,
    build_report_payload,
    write_report_outputs,
)
from app.secure_eval import run_workflow_secure
from multi_agent_system.types import MultiAgentState
from core.exceptions import ConfigurationError, ProviderError, AgentExecutionError
from core.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def _initial_state(repo_root: Path, eval_weights: Dict[str, int] | None = None) -> MultiAgentState:
    state = {
        "repo_root": repo_root,
        "shared_memory": {},
        "messages": [],
        "agent_results": {},
        "confidence_scores": {},
    }
    if eval_weights:
        state["eval_weights"] = eval_weights
    return state


def run_workflow(repo_root: Path, eval_weights: Dict[str, int] | None = None) -> Dict[str, Any]:
    """
    Run the full repository evaluation using the orchestrator and configured agents.
    
    Args:
        repo_root: Path to the repository to evaluate.
        eval_weights: Optional custom agent weighting configuration.
    
    Returns:
        dict: Final multi-agent state with evaluation results.
    
    Raises:
        ConfigurationError: If required configuration is missing or invalid.
        ProviderError: If external services fail (LLM providers, etc.).
        AgentExecutionError: If agent execution encounters errors.
    """
    try:
        logger.info(f"Starting evaluation workflow for repository: {repo_root}")
        graph = build_orchestrator()
        state = _initial_state(repo_root, eval_weights)
        result = graph.invoke(state)
        logger.info("Evaluation workflow completed successfully")
        return result
        
    except ConfigurationError as e:
        logger.warning(f"Configuration error during workflow: {e}")
        raise
    
    except ProviderError as e:
        logger.error(f"Provider failure during workflow: {e}", exc_info=True)
        raise
    
    except AgentExecutionError as e:
        logger.error(f"Agent execution failure: {e}", exc_info=True)
        raise
    
    except Exception as e:
        logger.exception("Unexpected error during workflow execution")
        raise AgentExecutionError(f"Workflow failed with unexpected error: {e}") from e


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point for Trust Bench repository evaluation.
    
    Args:
        argv: Command-line arguments (for testing).
    
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        description="Run the simplified Trust Bench multi-agent evaluation."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="Path to the repository to evaluate (default: current directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("multi_agent_output"),
        help="Directory where reports should be written (default: ./multi_agent_output).",
    )
    parser.add_argument(
        "--eval-weights",
        type=str,
        help="JSON string with evaluation weights for agents (e.g., '{\"security\": 40, \"quality\": 30, \"docs\": 30}').",
    )
    
    try:
        args = parser.parse_args(argv)

        repo_root = args.repo.resolve()
        if not repo_root.exists():
            logger.error(f"Repository directory does not exist: {repo_root}")
            print(f"[error] Repository directory does not exist: {repo_root}")
            return 1

        # Parse evaluation weights if provided
        eval_weights = None
        if args.eval_weights:
            try:
                eval_weights = json.loads(args.eval_weights)
                logger.debug(f"Parsed evaluation weights: {eval_weights}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON for eval-weights: {e}")
                print(f"[error] Invalid JSON for eval-weights: {e}")
                return 1

        # Run evaluation workflow
        final_state = run_workflow_secure(repo_root, eval_weights)
        report = build_report_payload(final_state)
        outputs = write_report_outputs(report, args.output.resolve())

        # Display results
        summary = report.get("summary", {})
        metrics = report.get("metrics", {})
        print("=== Multi-Agent Evaluation Complete ===")
        print(f"Repository: {report.get('repo_root')}")
        print(f"Overall Score: {summary.get('overall_score', 'n/a')}")
        print(f"Grade: {summary.get('grade', 'n/a')}")
        if metrics:
            print(
                f"System Latency: {metrics.get('system_latency_seconds', 'n/a')} seconds"
            )
            print(f"Faithfulness: {metrics.get('faithfulness', 'n/a')}")
            print(f"Refusal Accuracy: {metrics.get('refusal_accuracy', 'n/a')}")
        per_agent = metrics.get("per_agent_latency", {}) if metrics else {}
        if per_agent:
            print("Per-Agent Timings:")
            for agent, timing in per_agent.items():
                total = timing.get("total_seconds", "n/a")
                print(f"  - {agent}: {total} seconds")
        print(f"Report (JSON): {outputs['json']}")
        print(f"Report (Markdown): {outputs['markdown']}")
        
        logger.info("Evaluation completed successfully")
        return 0
    
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        print(f"[error] Configuration problem: {e}")
        print("Please check your environment variables and configuration.")
        return 2
    
    except ProviderError as e:
        logger.error(f"Provider error: {e}")
        print(f"[error] External service failure: {e}")
        print("LLM provider may be unavailable. Check API keys, network, or rate limits.")
        return 3
    
    except AgentExecutionError as e:
        logger.error(f"Agent execution error: {e}")
        print(f"[error] Agent encountered an error: {e}")
        print("Check logs for detailed error information.")
        return 4
    
    except Exception as e:
        logger.exception("Unexpected error in main execution")
        print(f"[error] Unexpected error: {e}")
        print("An internal error occurred. Check logs for details.")
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
