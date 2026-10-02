# Ten independent static source reviews

Model: `gpt-6-astra`; maximum four simultaneous workers. The selected main model was not changed.

The initial worktree-reading attempts were denied by host policy and are not counted as completed reviews. The successful retries reviewed explicit, sanitized source supplied via stdin, without executing tools or tests.

Reviews refer to the original sandbox source. They are findings, not certification of the later revision. Regression tests and GitHub Actions provide separate execution evidence.

## W01

W01 — Static review only; no tools used or tests executed.

1. **Unhandled integer overflow during inventory validation.**  
   References: `cron_master.py:106–109`, `cron_master.py:442–444`.  
   `math.isfinite()` converts integers to floating point. A valid JSON integer such as `10**400` raises `OverflowError`, which the CLI exception handler does not catch. One numeric field can abort the entire audit with a traceback instead of a structured rejection.

   Synthetic reproducer using supplied fixtures:
   ```python
   from test_cron_master import inv, job
   from cron_master import audit
   audit(inv(job(restart_count=10**400)))
   ```
   JSON equivalent: set `restart_count` to the unquoted decimal integer consisting of `1` followed by 400 zeros. Validate integers without float conversion, or reject oversized values explicitly.

2. **Null or non-object research checkpoints crash.**  
   References: `cron_master.py:396–399`, `cron_master.py:428–429`, `cron_master.py:442–444`.  
   `research_plan()` calls `.get()` without validating the checkpoint’s type. Valid JSON values including `null`, `[]`, and `1` cause an uncaught `AttributeError`.

   Exact synthetic reproducer:
   ```python
   from cron_master import research_plan
   research_plan(None)
   ```
   CLI equivalent: `research-plan checkpoint.json` with file contents `null`. Require an object before accessing fields.

3. **The JSON byte limit does not prevent nesting crashes.**  
   References: `cron_master.py:63–68`, `cron_master.py:442–444`.  
   Deeply nested JSON can raise `RecursionError` during decoding, before schema validation. That exception is uncaught, so a small hostile input bypasses structured error handling.

   Synthetic input:
   ```python
   payload = '[' * 100000 + '0' + ']' * 100000
   ```
   This is 200,001 bytes, below the five-million-byte limit. Supplying these bytes as the inventory file triggers decoder recursion failure under Python’s normal recursion limit. Handle excessive nesting as an input error.

— Mavis

## W02

W02 — static review only; no tools used or tests executed.

1. **Medium — receipt validation can combine two different file versions.** `cron_master.py:375–378` hashes bytes from the first read, then reopens the path through `load_json()` (`cron_master.py:63–68`). Promotion uses the second read’s `passed`, scope and target fields (`cron_master.py:379–388`), while the stored receipt retains the first version’s hash and asserts `integrity_checked=True` (`cron_master.py:389–392`).

   **Synthetic reproducer:** Create receipt A containing `{"scope":"sandbox","passed":false}` and supply A’s SHA-256 in a `sandbox_verified` lesson. Replace A with B containing `{"scope":"sandbox","passed":true}` after the hash comparison at line 376 but before the reread at line 378. The lesson is accepted with A’s hash although A reports failure. SQLite transaction atomicity does not protect these earlier filesystem reads.

   **Fix:** Parse and validate the exact bytes already hashed, preserving duplicate-key and invalid-number rejection.

For session checkpoints, I found no material CAS defect in the supplied implementation: `BEGIN IMMEDIATE` precedes the head read and comparison, and insertion remains within that transaction (`cron_master.py:315–329`).

Verification limits: the supplied tests cover orderly reopen and sequential stale writers (`tests/test_cron_master.py:167–182`), but do not demonstrate overlapping writers, abrupt termination, commit failures or backup restoration. No backup implementation is supplied, so backup correctness cannot be assessed.

— Mavis, W02

## W03

W03 — static review of supplied source only; no tools or executed testing.

1. **Medium — Receipts are not bound to the lesson’s claim or version.**  
   References: `cron_master.py:347–348,379–388`; `tests/test_cron_master.py:213–217`.  
   Promotion checks only the environment label (`sandbox`/`target`), `passed`, and, for target receipts, `target_id`. It never matches receipt evidence to the lesson’s claim or declared version scope. Exact-scope retrieval does not prevent evidence from being relabeled before storage.  
   **Synthetic reproducer:** Create a receipt containing `{"scope":"target","passed":true,"target_id":"TEST"}` with its correct SHA256. Record a `target_verified` lesson for `"Cronie version A"` on `TEST`; then reuse that receipt for a different claim under `"Cronie version B"`. Both pass the supplied validation, although the receipt establishes neither claim nor version.  
   **Fix:** Bind receipt contents to the claim or test identity and explicit product/version scope, and compare those fields during promotion.

2. **Medium — Receipt hashing and parsing use different file reads.**  
   References: `cron_master.py:375–380`; `cron_master.py:63–68`.  
   The code hashes `content`, then calls `load_json(path)`, reopening the file. A concurrent replacement can cause promotion using bytes that never matched the supplied hash, while the stored record reports `integrity_checked=True` (`cron_master.py:389`).  
   **Synthetic reproducer:** Initially supply a correctly hashed sandbox receipt with `passed:false`. Arrange for the file to become `{"scope":"sandbox","passed":true}` immediately before `load_json(path)` reads it. A `sandbox_verified` lesson passes despite its supplied hash covering the failed receipt.  
   **Fix:** Parse the already-hashed bytes with the same duplicate-key and invalid-number protections.

Authenticity boundary: `cron_master.py:389` explicitly records `authenticity:'not_attested'`. Caller-controlled source labels and malicious claim text alone therefore do not establish an authentication bypass or instruction execution.

— Mavis, W03

## W04

W04 — Static review only; no tools used or tests executed.

1. **Status namespaces collide, masking reported failures.**  
   References: `cron_master.py:132–140`, `cron_master.py:190–192`. Windows status decoding precedes explicit `result_semantics`, so an application result matching a scheduler constant bypasses application interpretation.  
   Synthetic reproducer using supplied fixtures:  
   `audit(inv(job(result_semantics='robocopy', last_result=0x41301)))`  
   Predicted result: `running_status` and `KEEP`, although the Robocopy branch would classify that value as `copy_failure_reported`. Generic application exit codes have the same ambiguity. Represent scheduler status and application exit results separately, or require an explicit namespace before decoding.

2. **Whitespace ownership bypasses the unowned deletion guard.**  
   References: `cron_master.py:110–112`, `cron_master.py:161`, `cron_master.py:183–184`, `cron_master.py:198–201`. Optional text validation permits whitespace-only owners, while ownership checks use truthiness.  
   Synthetic reproducer:  
   `actions(GovernanceTests().retirement(owner='   '))`  
   Predicted result: `DELETE_CANDIDATE`, with `protected_or_unowned=False`, despite having no meaningful owner identity. Reject or normalize blank ownership before applying every ownership gate.

3. **Contradictory disabled evidence silently receives KEEP.**  
   References: `cron_master.py:133–138`, `cron_master.py:185–192`, `cron_master.py:212–213`. A disabled scheduler status is decoded but never reconciled with the explicit enabled flag.  
   Synthetic reproducer:  
   `audit(inv(job(enabled=True, last_result=0x41302)))`  
   Predicted result: `disabled_status` alongside `KEEP`, without investigation of the conflicting evidence. Flag the discrepancy for reconciliation; do not infer which field represents current state.

These findings affect triage classifications. The supplied implementation still marks proposals unauthorized and performs no scheduler writes (`cron_master.py:174`, `cron_master.py:253–255`).

— Mavis / W04

## W05

W05 — Static review only; no tools used or tests executed.

1. **Medium — Input size limit is enforced after unbounded reading.**  
   `cron_master.py:63–68` reads the entire file before checking the 5 MB limit. A sufficiently large input can exhaust memory before the intended rejection, disrupting a calling subprocess.
   
   **Synthetic reproducer:** Supply a multi-gigabyte file as `large.json`; invoke `python cron_master.py audit large.json`. The entire file is read before validation.  
   **Fix:** Read at most `MAX_JSON_BYTES + 1` bytes, then reject oversized input.

2. **Medium — Malformed inputs escape the structured CLI error handler.**  
   `research_plan()` calls `.get()` without validating the checkpoint type (`cron_master.py:396–399`); its CLI caller accepts any JSON value (`428–429`). `AttributeError` is absent from the handler (`442–444`).
   
   **Synthetic reproducer:** `checkpoint.json` contains `[]`; invoke `python cron_master.py research-plan checkpoint.json`. The source implies an uncaught `AttributeError`, traceback on stderr, and exit code 1 instead of the handled JSON error and code 2. Deeply nested JSON similarly permits an uncaught `RecursionError` at `67–68`.  
   **Fix:** Validate checkpoint shape and explicitly handle parser recursion failures.

3. **Medium — Read commands silently create missing databases and report success.**  
   `cron_master.py:430–435` constructs `Ledger` for `session-show` and `lesson-list`. Construction creates parent directories, a database, and tables (`278–291`). Thus a mistyped or missing database path becomes an empty ledger rather than a reported missing-file error.
   
   **Synthetic reproducer:** With `missing/state.sqlite` absent, invoke `python cron_master.py session-show --db missing/state.sqlite`. The source implies filesystem creation, stdout `null`, and exit code 0 (`440–441`), potentially masking lost continuity.  
   **Fix:** Open existing databases without creation for read commands; reserve initialization for explicit creation or recording.

— Mavis, W05

## W06

W06 — Static review only; no tools used or tests executed.

1. **Runtime isolation depends on launch settings absent from the supplied source.** `Dockerfile:7` enforces a non-root default user, but `Dockerfile:1–8` provides no runtime enforcement of a read-only root filesystem or network denial. An ordinary launch retains Docker’s default writable filesystem and networking. This does **not** establish that an external launcher omits those controls.
   **Synthetic reproducer:** Build as `w06-review`, then run:
   ```sh
   docker run --rm w06-review python -c "import pathlib,socket; pathlib.Path('/tmp/probe').write_text('writable'); print(socket.getaddrinfo('example.com',443))"
   ```
   Without external restrictions, the write succeeds and DNS resolution is permitted.
   **Remedy:** Require launch options such as `--read-only --network none`, with an explicitly bounded temporary filesystem if tests need one.

2. **Dependency installation is not fully locked or artifact-verified.** `Dockerfile:5` installs dependencies as root before `USER` at `Dockerfile:7`. `requirements-test.txt:1–3` pins three direct versions but supplies neither artifact hashes nor a complete transitive lock. Dependency resolution can therefore change as compatible transitive releases become available; `--no-cache-dir` does not prevent that.
   **Synthetic reproducer:** In a controlled package index, let a pinned direct package require `child>=1`; build once with `child==1` available, then rebuild without Docker layer caching after adding `child==2`. The unchanged requirements can produce different installed environments.
   **Remedy:** Lock the complete dependency graph and install with `--require-hashes`.

No shared-cache mutation is demonstrated by the supplied files: pip caching is explicitly disabled, and no shared-cache mount is shown.

— Mavis, W06

## W07

W07 — Static source review only; no tools used or tests executed.

1. **Low — Valid boundary dates can crash `time-check` outside its structured error handling.**  
   References: `cron_master.py:260–267`, `cron_master.py:442–444`. Converting an accepted local datetime to UTC can exceed Python’s supported year range and raise `OverflowError`, which the CLI does not catch.

   Synthetic reproducer:
   ```text
   python cron_master.py time-check 9999-12-31T23:30:00 --zone Etc/GMT+1
   ```
   Assuming that IANA zone is installed, its UTC−01:00 offset requires a UTC instant in year 10000. Predicted result: an uncaught traceback instead of the structured JSON error and exit code 2. Catch `OverflowError` or explicitly reject unrepresentable conversions.

No other material defect identified within scope. Cron parsing and scheduler DST policy are explicitly unsupported (`cron_master.py:254`, `259`, `427`). Freshness intentionally accepts ages from zero through the configured maximum, inclusive, and rejects future timestamps for candidate proposals (`cron_master.py:155–167`); no clock-skew tolerance is promised.

The supplied tests cover Montréal’s spring gap and autumn fold, but omit exact freshness thresholds and datetime-range overflow (`tests/test_cron_master.py:102–110`, `145–151`; `tests/test_swarm_regressions.py:8–15`).

— Mavis / W07

## W08

W08 — Static review only; no tools used or tests executed.

**No material findings established from the supplied source.**

- **Secrets and live data:** No apparent embedded credentials or production inventories were identified. Test fixtures use synthetic identities and temporary ledger storage (`tests/test_cron_master.py:16–24,154–165`; `tests/test_w5_regressions.py:35–41`). Common environment files, state directories, databases and generated artifacts are ignored (`.gitignore:5–16`).
- **Privacy boundary:** Inputs are not sanitized for publication: evidence is copied into proposals (`cron_master.py:168–174`), and session data is stored and returned (`cron_master.py:312–325`). This matches an explicit prohibition on supplying secrets or production inventories, rather than a promise of redaction (`SECURITY.md:3`). Outputs therefore should not be presumed publication-safe.
- **Release claims:** Documentation explicitly limits the release to a sandbox preview and disclaims production certification (`README.md:3,7,17`). Research plans report `executed: False` (`cron_master.py:396–404`).

Repository history, tracked-file exclusions, CI configuration and actual release contents were not supplied; their safety cannot be established here. No defect reproducer is asserted because no material defect was established.

— Mavis, W08

## W09

Static review only; no tools used and no tests executed.

1. **Medium — Expected failures can produce a false green.**  
   `eval/run_case.py:22–24` accepts `result.wasSuccessful()` with one test and no skips, but does not inspect or report `result.expectedFailures`. Python’s `unittest` treats an expected failure as successful. `eval/assert-component.cjs:7–9` therefore accepts that result: `passed=true`, `tests_run=1`, and zero skips, failures, and errors.

   **Synthetic reproducer:** In an isolated fixture, replace the allowlisted test’s implementation with:
   ```python
   @unittest.expectedFailure
   def test_robocopy_three_is_not_failure(self):
       self.fail("Regression deliberately present")
   ```
   The adapter would report a passing result despite the failed assertion. This also undermines the negative control configured at `eval/negative-control.json:24–26`: an expected failure could make the deliberately broken classifier appear green.

   **Fix:** Require `not result.expectedFailures` when computing `passed`; report an `expected_failures` count and require it to equal zero in the external assertion.

No additional material defect is established by the supplied source. Explicit skips are rejected by both the adapter and assertion (`eval/run_case.py:22–23`; `eval/assert-component.cjs:7`). The provider checks an own-property allowlist and uses argument-based execution with `shell: false` (`eval/provider.mjs:14–19`). The actual allowlist, test body, and automation interpreting the negative-control outcome were not supplied, so their correctness remains unverified.

— Mavis / W09

## W10

W10 — Static review only; no tools used or tests executed.

1. **Receipt integrity has a read/replace race.** `cron_master.py:375–378` hashes one read, then `load_json(path)` reads the file again. Promotion uses the second contents (`cron_master.py:379–389`), so `integrity_checked=True` can describe bytes different from those hashed. Existing hash tests cover only unchanged files (`tests/test_cron_master.py:190–195`).
   **Synthetic reproducer:** Supply the hash of a receipt containing `passed:false`; replace it with a same-scope `passed:true` receipt immediately before `load_json` reads it. The supplied control flow permits promotion. Add a deterministic replacement regression; parse the already-hashed bytes. This concerns integrity, even though authenticity is correctly marked unattested.

2. **Ledger tests do not establish overlapping-write or crash-recovery guarantees.** The two-connection test executes writes sequentially (`tests/test_cron_master.py:177–182`); the swarm regression checks a mock call count without another writer (`tests/test_swarm_regressions.py:29–33`). Neither establishes C14’s overlapping-worker requirement or C11’s interrupted continuity requirement (`evaluation-rubric.json:78–79,99–100`). This is an evidence gap, not a demonstrated SQLite defect.
   **Synthetic reproducer:** Release two independently connected processes from a barrier with the same predecessor; require exactly one committed successor and an explicit loser error. Separately terminate a writer before commit and after commit/before acknowledgement (`cron_master.py:324–330`), reopen, and verify head integrity and explicit reconciliation without duplicate continuation.

3. **DST examples cannot satisfy the schedule-semantics gate.** Tests cover a few wall-clock conversions (`tests/test_cron_master.py:145–151`), while the implementation explicitly excludes cron parsing and leaves scheduler policy unevaluated (`cron_master.py:258–269,423–427`). C17 requires dialect-specific concrete firing times (`evaluation-rubric.json:120–121`).
   **Synthetic reproducer:** Compare five-field and six-field schedules, nonexistent/ambiguous local times, and calendar boundaries against declared scheduler policies. The current interface cannot perform that evaluation; round-trip property tests would strengthen conversion coverage but would not close C17.

Release limitations are stated honestly (`README.md:3–7,17`; `evaluation-rubric.json:176–178`). Retain the blocked workflow/target acceptance status.

— Mavis / W10
