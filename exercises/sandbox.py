"""The isolated Docker-based pytest judge used by generation tasks."""
import subprocess
import tempfile
from pathlib import Path

from .models import Candidate

SANDBOX_IMAGE = "whetstone-sandbox:latest"


def judge(candidate: Candidate) -> tuple[str, str]:
    """Judge a candidate without allowing its code network or write access.

    The host only gives Docker a read-only directory containing these two files.
    Docker's timeout is enforced by the parent Python process after 10 seconds.
    """
    if candidate.verdict == Candidate.Verdict.ERROR:
        return candidate.verdict, candidate.failure_reason

    with tempfile.TemporaryDirectory(prefix="whetstone-judge-") as directory:
        workdir = Path(directory)
        solution = workdir / "solution.py"
        tests = workdir / "test_solution.py"
        solution.write_text(candidate.reference_solution, encoding="utf-8")
        tests.write_text(candidate.test_source, encoding="utf-8")
        workdir.chmod(0o755)
        solution.chmod(0o444)
        tests.chmod(0o444)
        command = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--read-only",
            "--pids-limit", "64",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--user", "65534:65534",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "--mount", f"type=bind,src={workdir},dst=/workspace,readonly",
            "--workdir", "/workspace",
            "--env", "PYTHONDONTWRITEBYTECODE=1",
            SANDBOX_IMAGE,
            "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_solution.py",
        ]
        try:
            result = subprocess.run(command, text=True, capture_output=True, timeout=10, check=False)
        except subprocess.TimeoutExpired:
            return Candidate.Verdict.FAIL, "Judge timed out after 10 seconds."
        except OSError as exc:
            return Candidate.Verdict.FAIL, f"Sandbox failed to start: {exc}"

    if result.returncode == 0:
        return Candidate.Verdict.PASS, ""
    output = (result.stdout + "\n" + result.stderr).strip()
    return Candidate.Verdict.FAIL, output[-4000:] or f"Sandbox exited with status {result.returncode}."
