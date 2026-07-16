"""Prove the sandbox passes correct code, fails wrong code, and kills hangs."""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whetstone.settings")
django.setup()

from exercises.models import Candidate, GenerationRun
from exercises.sandbox import judge

run = GenerationRun.objects.create(topic="harness check", difficulty="beginner", requested_count=3)

CASES = [
    ("correct", "def solve(n):\n    return n * 2\n",
     "from solution import solve\n\ndef test_double():\n    assert solve(3) == 6\n"),
    ("wrong", "def solve(n):\n    return n * 3\n",
     "from solution import solve\n\ndef test_double():\n    assert solve(3) == 6\n"),
    ("hang", "def solve(n):\n    while True:\n        pass\n",
     "from solution import solve\n\ndef test_double():\n    assert solve(3) == 6\n"),
]

for label, solution, tests in CASES:
    c = Candidate.objects.create(
        generation_run=run, attempt_number=1,
        problem_statement=f"harness: {label}",
        reference_solution=solution, test_source=tests,
    )
    verdict, reason = judge(c)
    print(f"\n=== {label} -> {verdict}")
    print(reason[:400] if reason else "(no reason)")