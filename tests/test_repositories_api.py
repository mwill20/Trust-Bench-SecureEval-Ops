from fastapi.testclient import TestClient

from trust_bench_studio.api import repositories
from trust_bench_studio.api.server import app
from trust_bench_studio.services import GitHubService, JobManager, JobStore


def test_analyze_and_status_endpoints(tmp_path):
    original_manager = repositories.job_manager
    store_root = tmp_path / "jobs"
    store = JobStore(root=store_root)
    github = GitHubService(workspaces_root=store_root)
    repositories.job_manager = JobManager(store=store, github_service=github)

    client = TestClient(app)
    try:
        payload = {"repo_url": "https://github.com/example/repo"}
        response = client.post("/api/repositories/analyze", json=payload)
        assert response.status_code == 200, response.text
        job_payload = response.json()["job"]
        assert job_payload["repo_url"] == "https://github.com/example/repo"
        assert job_payload["state"] == "queued"
        job_id = job_payload["id"]

        status_resp = client.get(f"/api/repositories/{job_id}/status")
        assert status_resp.status_code == 200, status_resp.text
        status_payload = status_resp.json()["job"]
        assert status_payload["id"] == job_id
        assert status_payload["metadata"]["status"] == "pending_clone"
    finally:
        repositories.job_manager = original_manager
