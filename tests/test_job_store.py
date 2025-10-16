from pathlib import Path

from trust_bench_studio.services import (
    GitHubService,
    JobManager,
    JobStage,
    JobState,
    JobStore,
)


def test_job_store_persistence(tmp_path):
    store = JobStore(root=tmp_path)
    job = store.create_job("https://github.com/example/repo", profile="default")

    assert job.state is JobState.QUEUED
    assert job.stage is JobStage.INIT
    assert Path(tmp_path / job.id / JobStore.STATUS_FILENAME).exists()

    store.update_job(job.id, state=JobState.CLONING, stage=JobStage.CLONING, progress=0.15)
    reloaded = JobStore(root=tmp_path).get_job(job.id)
    assert reloaded is not None
    assert reloaded.state is JobState.CLONING
    assert reloaded.stage is JobStage.CLONING
    assert reloaded.progress == 0.15


def test_job_manager_allocates_workspace(tmp_path):
    store = JobStore(root=tmp_path)
    github = GitHubService(workspaces_root=tmp_path)
    manager = JobManager(store=store, github_service=github)

    job = manager.enqueue("https://github.com/example/repo.git")
    assert job is not None
    workspace = Path(job.metadata["workspace"])
    assert workspace.exists()
    assert workspace.is_dir()
    assert job.metadata["status"] == "pending_clone"
    assert job.message == "Job queued for analysis"
