"""Simple job processor for repository analysis demo."""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

from trust_bench_studio.services import JobManager, JobState, JobStage


class SimpleJobProcessor:
    """Demo job processor for repository analysis."""
    
    def __init__(self):
        self.job_manager = JobManager()
    
    async def process_job(self, job_id: str) -> None:
        """Process a single job through all stages."""
        try:
            # Stage 1: Cloning
            self.job_manager.transition(
                job_id,
                state=JobState.CLONING,
                stage=JobStage.CLONING,
                progress=0.1,
                message="Cloning repository..."
            )
            await asyncio.sleep(2)  # Simulate cloning time
            
            # Stage 2: Analysis
            self.job_manager.transition(
                job_id,
                state=JobState.ANALYZING,
                stage=JobStage.ANALYSIS,
                progress=0.3,
                message="Analyzing code structure..."
            )
            await asyncio.sleep(3)  # Simulate analysis time
            
            # Stage 3: Evaluation
            self.job_manager.transition(
                job_id,
                state=JobState.EVALUATING,
                stage=JobStage.EVALUATION,
                progress=0.6,
                message="Running security and quality checks..."
            )
            await asyncio.sleep(4)  # Simulate evaluation time
            
            # Stage 4: Reporting
            self.job_manager.transition(
                job_id,
                state=JobState.REPORTING,
                stage=JobStage.REPORTING,
                progress=0.9,
                message="Generating analysis reports..."
            )
            await asyncio.sleep(2)  # Simulate reporting time
            
            # Stage 5: Complete
            artifacts = {
                "security_score": 85,
                "code_quality": 78,
                "documentation": 92,
                "test_coverage": 65,
                "issues_found": [
                    "SQL injection vulnerability in auth.py:142",
                    "Missing input validation in api/users.py:89", 
                    "Hardcoded API key in config/settings.py:15"
                ],
                "recommendations": [
                    "Add parameterized queries for database access",
                    "Implement comprehensive input validation",
                    "Use environment variables for sensitive data"
                ]
            }
            
            self.job_manager.transition(
                job_id,
                state=JobState.COMPLETE,
                stage=JobStage.COMPLETE,
                progress=1.0,
                message="Analysis completed successfully",
                artifacts=artifacts
            )
            
        except Exception as e:
            self.job_manager.transition(
                job_id,
                state=JobState.FAILED,
                stage=JobStage.INIT,
                progress=0.0,
                message=f"Analysis failed: {str(e)}",
                error=str(e)
            )


async def process_pending_jobs():
    """Check for pending jobs and process them."""
    processor = SimpleJobProcessor()
    print("Job processor ready - monitoring for new repository analysis jobs...")
    
    processed_jobs = set()  # Track processed jobs to avoid reprocessing
    
    while True:
        try:
            # Get all jobs and find ones that need processing
            for job in processor.job_manager.list():
                if (job.state == JobState.QUEUED and 
                    job.stage == JobStage.INIT and 
                    job.id not in processed_jobs):
                    
                    print(f"[{time.strftime('%H:%M:%S')}] Processing job {job.id[:8]}...")
                    print(f"  Repository: {job.repo_url}")
                    
                    processed_jobs.add(job.id)
                    await processor.process_job(job.id)
                    
                    print(f"[{time.strftime('%H:%M:%S')}] Job {job.id[:8]} completed successfully!")
                    
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error in job processor: {e}")
            
        await asyncio.sleep(3)  # Check every 3 seconds


if __name__ == "__main__":
    print("Trust Bench Repository Analysis Worker")
    print("=====================================")
    try:
        asyncio.run(process_pending_jobs())
    except KeyboardInterrupt:
        print("\nJob processor stopped.")
    except Exception as e:
        print(f"\nJob processor crashed: {e}")