# Whetstone

Coding exercises that carry proof of their own solvability.

A language model writing a coding exercise has no way to know whether the exercise
can be solved. It ships a broken problem with the same confidence it ships a good
one. An instructor pastes twenty generated problems into a worksheet, three cannot
be solved, and a student burns an evening on problem 14 believing the failure is
their own.

Whetstone makes the model earn the problem. Codex generates a candidate exercise,
a reference solution, and the test suite that will judge that solution. A sandbox
runs the solution against those tests. Pass, and the exercise reaches a student.
Fail, and it drops into a discard log with its reason. The value of the product
comes from what it throws away.

## What the numbers show

Across sixty generated candidates, fifty-nine passed their own tests and one
failed. That one asked for a function to validate an identity matrix. The model's
own reference solution shadowed a loop variable and crashed with
`TypeError: object of type 'int' has no len()`. The problem statement read fine.
The tests read fine. Only execution caught it. A student would have solved it
correctly and been told they were wrong.

A frontier model writes solvable exercises almost every time. Almost is exactly
why verification matters. Whetstone catches the one in sixty that would have
reached a student.

## Architecture

- **Django and PostgreSQL** carry the generate-and-verify loop and store every
  candidate, kept or discarded.
- **Flutter Web** renders the corpus: the generated/kept/discarded count, the
  discard log with failure reasons, and the published exercises.
- **Docker sandbox** judges each candidate in isolation: no network, read-only
  filesystem, dropped capabilities, non-root user, a hard timeout that kills
  infinite loops, and a memory cap. `exercises/sandbox.py` holds the judge.

The data model stays small. `GenerationRun` holds a request. `Candidate` holds a
problem statement, reference solution, test source, verdict, and failure reason.
`Exercise` holds a survivor. Discard rate is a query over `Candidate`, never a
stored number.

## Proving the sandbox is sealed

The judge disables container networking. This test runs deliberately
network-dependent code through the same restrictions the judge uses:

    docker run --rm --network none --memory 512m --read-only \
      --tmpfs /tmp:rw,noexec,nosuid,size=64m \
      whetstone-sandbox:latest \
      python -c "import socket; socket.create_connection(('1.1.1.1', 53), 2)"

It fails with a network-unreachable error. A generated candidate that tries to
reach the network fails its tests and is retained in the discard log with that
reason, never published.

## How I built this with Codex and GPT-5.6

Codex wrote the core of the generate-and-verify loop: the generation call, the
candidate model, and the sandbox judge. Working inside one Codex thread, I moved
from an empty schema to a proven loop that passes correct solutions, fails wrong
ones, and kills hanging code.

The product and engineering decisions were mine. I chose to show the discard log
rather than hide it as a debug artifact, because a discard log is the clearest
three-second explanation of why the kept exercises are trustworthy. I froze the
sandbox contract so the judge could not be talked out of a verdict. I set the
isolation flags on the Docker container after reasoning about what model-written
code could do to the host.

Midway through the build, my hackathon credits turned out to be Codex credits
rather than OpenAI Platform API credits, so a live generation endpoint was not
funded. I moved generation into Codex itself and kept the sandbox as the only
judge. The product did not change. Codex generated the candidates, the sandbox
ruled on them, and the corpus carries the same proof it always would have. The
finding held: sixty generated, fifty-nine kept, one caught.

The live-generation path built earlier in the week (a Celery worker calling the
API, in `tasks.py` and `exercises/management/commands/`) remains in the codebase.
The deployed demo runs the Codex-built corpus through the same sandbox.

## Running it

The backend reads configuration from environment variables and runs on Django
with PostgreSQL. The sandbox requires Docker. The Flutter frontend is built for
web and served as static files, with the API base URL set at build time.

Both halves are deployed and reachable. Testing instructions and live URLs are in
the Devpost submission.

## Codex Session ID

`019f675e-b148-7581-9b49-c3b63a606fff`
