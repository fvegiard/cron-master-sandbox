# Cron Master Sandbox

Public, **sandbox-only preview** of a deterministic read-only scheduler audit core and 24-point evaluation contract. It does not start a queen daemon, execute schedules, mutate schedulers, or authorize actions.

Validation is performed on synthetic data in disposable GitHub-hosted machines. No self-hosted runner, private inventory, credentials, live session databases, or shared browser caches belong in this repository.

The original local agent activation was deactivated before this sandbox was prepared. Existing component results are historical, not proof of this repository revision. See Actions for actual run status.

## Development checks

`python -m unittest discover -s tests -v`

Windows needs IANA data: install the pinned `tzdata` dependency only inside an isolated environment.

## Safety

No deployment, cron trigger, scheduler write or autonomous background operation is included. Candidate findings always require independently verified evidence and appropriate authorization. Passing tests do not certify production safety or all 24 workflow gates.
