# Isolation and validation plan

1. Deactivate local role/skill entry points; preserve dated rollback copies.
2. Stage only allowlisted code and synthetic tests. Exclude personal paths, logs, state and credentials.
3. Obtain ten independent bounded read-only reviews in separate worktrees; queen alone integrates.
4. Reproduce reported faults with regression tests before patching. Test input validation, scope, status codes, timezones, transaction races, restart, CLI, negative controls, privacy and sandbox containment.
5. Execute cross-platform tests on disposable GitHub-hosted VMs and a non-root, read-only, network-disabled Docker container. Pin actions to verified commit IDs. No real scheduler jobs.
6. Publish inspectable CI evidence and remaining limitations; keep local activation disabled.
