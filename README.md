# Cron Master Sandbox

A public **sandbox-only preview**, not an activated queen, production scheduler, or autonomous repair service. The original local role/skill entry points were disabled before this work. This repository contains no live inventories, credentials, session databases, or active agent configuration.

## Run in the isolated container

Build-time dependency downloads need network access; the test runtime does not:

```sh
docker build -t cron-master-sandbox .
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 --memory 1g --cpus 2 --tmpfs /tmp:rw,nosuid,nodev,size=268435456 cron-master-sandbox
```

The default command verifies non-root execution, read-only root, dropped capabilities, no-new-privileges, a denied outbound connection, checks for common host/socket paths and a writable temporary area before running synthetic tests. CI separately verifies that no bind mounts were configured. Do not mount private folders or pass credentials. The Docker base digest and complete Python test dependencies are pinned; wheel hashes are required. Promptfoo's direct version is pinned, but its npm transitive dependency lock is not yet committed.

## Python-only development checks

These are component tests, not an operating-system sandbox. Use a disposable machine or the container for untrusted input:

```sh
python -m venv .venv
# Linux/macOS:
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-test.lock
.venv/bin/python scripts/run_ci.py
# Windows PowerShell uses .venv\Scripts\python.exe in place of .venv/bin/python.
```

## Evidence and limits

The expanded tests cover input validation, timezone conversion, status interpretation, evidence integrity, concurrency, recovery and evaluation correctness. CI results and artifacts are available at https://github.com/fvegiard/cron-master-sandbox/actions.

Ten static source reviews are recorded in docs/STATIC-REVIEWS.md. Primary references and action pins are in docs/PRIMARY-SOURCES.md and docs/action-pins.json.

The 24-point contract in EVALUATION-24.md is broader than component testing. A green run is not certification of a production autonomous agent. Native scheduler execution, complete backend discovery and a persistent queen dispatcher remain outside this preview. Cloud browser evidence does not establish recovery of any personal computer.
