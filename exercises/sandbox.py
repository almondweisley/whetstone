"""The isolated Docker-based pytest judge used by generation tasks."""
import subprocess
import tempfile
import uuid
from pathlib import Path

from .models import Candidate

SANDBOX_IMAGE = "whetstone-sandbox:latest"
INNER_TIMEOUT = 10
OUTER_TIMEOUT = 15


def judge(candidate: Candidate) -> tuple[str, str]:
    """Judge a candidate without allowing its code network or write access.

    The host only gives Docker a read-only directory containing these two files.
    The container enforces its own limit, and the parent process backstops it.
    """
    if candidate.verdict == Candidate.Verdict.ERROR:
        return candidate.verdict, candidate.failure_reason

    name = f"whetstone-{uuid.uuid4().hex[:12]}"

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
            "--name", name,
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1.0",
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
            "timeout", "--signal=KILL", str(INNER_TIMEOUT),
            "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_solution.py",
        ]
        try:
            result = subprocess.run(
                command, text=True, capture_output=True, timeout=OUTER_TIMEOUT, check=False
            )
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", name], capture_output=True, check=False)
            return Candidate.Verdict.FAIL, f"Judge timed out after {OUTER_TIMEOUT} seconds."
        except OSError as exc:
            subprocess.run(["docker", "kill", name], capture_output=True, check=False)
            return Candidate.Verdict.FAIL, f"Sandbox failed to start: {exc}"

    if result.returncode == 0:
        return Candidate.Verdict.PASS, ""
    if result.returncode == 137:
        return Candidate.Verdict.FAIL, f"Solution did not finish within {INNER_TIMEOUT} seconds."
    output = (result.stdout + "\n" + result.stderr).strip()
    return Candidate.Verdict.FAIL, output[-4000:] or f"Sandbox exited with status {result.returncode}."