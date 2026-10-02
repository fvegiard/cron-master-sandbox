# Primary research sources

Consulted on 2026-10-02. Source documentation informs design; it does not replace execution evidence or certify a production deployment. Versions actually executed are recorded by CI.

1. OpenAI subagent documentation: https://developers.openai.com/codex/subagents
2. OpenAI skill documentation: https://developers.openai.com/codex/skills
3. GitHub CLI repository creation: https://cli.github.com/manual/gh_repo_create
4. GitHub-hosted runner isolation: https://docs.github.com/actions/using-github-hosted-runners/about-github-hosted-runners
5. GitHub runner operating systems: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
6. GitHub Actions secure use: https://docs.github.com/en/actions/reference/security/secure-use
7. GitHub workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
8. GitHub context availability: https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
9. GitHub workflow-run evidence: https://docs.github.com/en/actions/how-tos/monitor-workflows/view-workflow-run-history
10. Docker runtime security controls: https://docs.docker.com/engine/containers/run/
11. Docker seccomp: https://docs.docker.com/engine/security/seccomp/
12. Docker rootless architecture: https://docs.docker.com/engine/security/rootless/
13. Docker image manifest inspection: https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/
14. Python JSON limitations: https://docs.python.org/3/library/json.html
15. Python SQLite and URI access: https://docs.python.org/3/library/sqlite3.html
16. Python unittest expected-failure semantics: https://docs.python.org/3/library/unittest.html
17. Python process invocation: https://docs.python.org/3/library/subprocess.html
18. Python IANA timezone handling: https://docs.python.org/3/library/zoneinfo.html
19. Python concurrency: https://docs.python.org/3/library/concurrent.futures.html
20. SQLite transaction semantics: https://sqlite.org/lang_transaction.html
21. SQLite backup API: https://sqlite.org/backup.html
22. Hypothesis testing: https://hypothesis.readthedocs.io/en/latest/quickstart.html
23. Coverage branch measurement: https://coverage.readthedocs.io/en/latest/branch.html
24. Coverage subprocess measurement: https://coverage.readthedocs.io/en/latest/subprocess.html
25. pip hash-checked installations: https://pip.pypa.io/en/stable/topics/secure-installs/
26. Promptfoo external JavaScript assertions: https://www.promptfoo.dev/docs/configuration/expected-outputs/javascript/
27. Promptfoo assertion contracts: https://www.promptfoo.dev/docs/configuration/expected-outputs/
28. Playwright browser installation and cache lifecycle: https://playwright.dev/docs/browsers
29. Playwright library isolation: https://playwright.dev/docs/library
30. Playwright browser launch boundaries: https://playwright.dev/docs/api/class-browsertype
31. Playwright browser lifecycle: https://playwright.dev/docs/api/class-browser

Exact action commit pins are in `action-pins.json`. Exact Python wheel hashes and release metadata are in `requirements-test.lock` and `python-dependency-provenance.json`. PyPI metadata hashes protect subsequent installation integrity, not the trustworthiness of upstream code.
