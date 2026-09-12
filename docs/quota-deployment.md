# Quota design and Cloud Run deployment

A budget is a fixed window, not a rolling delay. Daily windows start at UTC midnight.
The database unique key gives each identity one counter per endpoint and window.
A conditional upsert reserves a slot only below the limit. Rejected requests do not
increase the counter. Login reserves before looking up a user or checking a password;
a successful login refunds that exact window. Failures keep the reservation. Concurrent
in-flight logins occupy slots, so a correct password can receive 429 while the budget
is exhausted. This is intentional: blocked guesses must not be tested.

Guest chat consumes both a source budget and a token budget. Minting a token does not
reset the source budget. Source is charged first; a later rejection or model failure
still consumes it. Shared NAT users share this budget. IP rotation remains possible;
use ingress abuse controls for distributed attacks. Guest issuance itself makes no
model or database calls. Login email/IP tuples are hashed, not truncated.

All quota operations own their session. Async chat offloads them to a worker thread;
synchronous auth handlers run in FastAPI's thread pool. Quota database errors return
503 without calling the model or issuing a login token. Connect, pool, statement and
lock waits are bounded. Retry-After accompanies exhausted budgets.

## Deployment sequence

1. Use a separate migration job with the target database and the new image. Verify
   `SHOW TimeZone` is UTC and that existing quota rows were written under UTC.
   If previous writers used another time zone, stop and reconcile those timestamps
   before this migration; its conversion explicitly assumes UTC. Pause old writers
   during the timestamp conversion. The ALTER TABLE and index creation can take locks;
   schedule a maintenance window for a large existing table.
2. Run `uv run alembic upgrade head`. Verify revision `c13a00000001`, the timestamptz
   column, the unique constraint, and the window_start index before routing traffic.
   The health endpoint does not certify schema readiness.
3. Set `TRUSTED_PROXY_CIDRS` to the verified immediate and intermediate proxy networks
   for your actual ingress. The container disables Uvicorn proxy rewriting: the app
   walks X-Forwarded-For from the real socket peer, right to left, stopping at the first
   untrusted address. Never use `0.0.0.0/0` or `::/0`. Empty trust is for direct local
   connections only. Restrict ingress to the intended Cloud Run/load-balancer path;
   do not guess Google proxy ranges. Validate this in staging before accepting traffic.
4. From two real client addresses, confirm independent registration budgets. Supply a
   forged leftmost header and confirm it cannot change the derived source. Exercise
   multiple instances concurrently, exhausted login, renewed guest tokens, window
   rollover, and database outages while health requests remain responsive.
5. Create a Cloud Run job from the same image with command `uv run python -m
   app.jobs.cleanup_quotas`, scheduled hourly by Cloud Scheduler. Use the same window
   settings as the service. Keep the largest window used by any still-running revision
   until that revision is retired. Each run deletes at most 100,000 old rows in batches
   of 1,000, skipping locked rows. Retention is the longest window plus
   `QUOTA_RETENTION_SECONDS` (default one extra day). Alert on job failures or a growing
   backlog; increase schedule frequency if necessary.

Application rollback may keep the additive table and timezone-aware column. Do not
run schema downgrade while newer revisions use them. Avoid routing back to the original
vulnerable quota implementation. No automatic retry is made after an ambiguous commit:
a request may have consumed a slot even if it received 503.

## Tests

Run `uv run python -m unittest discover -s tests`. PostgreSQL integration tests use
`QUOTA_TEST_DATABASE_URL` pointing to an explicitly disposable PostgreSQL database;
never use production. They exercise real concurrent upserts and time-zone consistency.
