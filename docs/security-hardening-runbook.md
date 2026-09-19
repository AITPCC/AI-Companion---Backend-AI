# Security hardening runbook

This is a practical rollout guide for the AI Companion FastAPI service on Cloud Run. It assumes the API is called directly by iOS and Android apps.

## Important decision: keep Google Cloud IAM off the mobile-client path

Do **not** change the Cloud Run service to **Require authentication** while the mobile apps call it directly. That setting requires a Google IAM identity token, which a mobile app cannot keep secret. It would break the app, and embedding a service-account credential in an app is unsafe.

The service can remain publicly *reachable*. Registered users should use the app's bearer token. Guests can still use free chat, but they need a short-lived, server-issued **guest session token** with a small quota. In the current code, `/chat/completions` accepts completely anonymous requests with no quota, so it is the first item to fix.

Later, place a Google HTTPS load balancer and Cloud Armor in front of it, then restrict Cloud Run ingress to **Internal and Cloud Load Balancing**. Mobile clients still reach the public load-balancer URL; they no longer reach the `run.app` URL directly.

## Before starting

1. Create a change ticket and choose a quiet deployment window.
2. Identify the Cloud project, region, service name, and production custom domain. The examples use these placeholders:

   ```bash
   export PROJECT_ID="YOUR_PROJECT_ID"
   export REGION="asia-southeast1"
   export SERVICE="ai-companion-backend"
   ```

3. Use a non-production project or Cloud Run revision to test each change first.
4. Never paste `GOOGLE_API_KEY`, `JWT_SECRET_KEY`, database URLs, access tokens, or customer prompts into tickets, shells saved to history, source code, or logs.

## Phase 0 — verify the alert (today, 30–60 minutes)

The `.env` and `phpinfo.php` requests in the alert are common opportunistic internet scans. The shown `404` responses mean those individual requests did not retrieve a file. They are not, by themselves, proof of compromise.

### 0.1 Look for successful or suspicious requests

In **Cloud Logging > Logs Explorer**, select the Cloud Run service and run a query similar to this. Adjust the service name and time range.

```
resource.type="cloud_run_revision"
resource.labels.service_name="ai-companion-backend"
httpRequest.status >= 200
httpRequest.status < 400
(httpRequest.requestUrl =~ ".*\\.env.*" OR
 httpRequest.requestUrl =~ ".*phpinfo.*" OR
 httpRequest.requestUrl =~ ".*\\.git.*" OR
 httpRequest.requestUrl =~ ".*backup.*")
```

Also check for sudden increases in `/chat/completions`, `/auth/login`, `/auth/register`, 5xx responses, Cloud Run instance count, and the Gemini/API-provider bill.

### 0.2 Decide whether to rotate secrets

Rotate a secret immediately if a sensitive file returned `200`/`30x`, a secret appeared in a log/image/repository, or there is another credible exposure. If all relevant probes are confirmed `404` and secrets were never exposed, record the result; do not rotate solely because a scanner asked for a file.

If rotating, create a new Secret Manager version, deploy a new revision referencing it, validate the service, then disable the old version after the rollback window. Rotate the Google AI key, JWT signing key, and database password independently so problems can be rolled back safely.

## Phase 1 — protect the FastAPI application (today)

### 1.1 Require a registered-user or guest-session token for chat

Do not require registered login for free guest chat. Instead, add a public `POST /auth/guest-session` endpoint that issues a short-lived, signed guest token. The mobile app calls it when it first opens chat, stores it only in secure device storage, and sends it as a bearer token to chat.

The guest token is **not** a secret that proves a real identity. Its purpose is to give the server a temporary quota key and make bulk abuse more expensive. Do not accept a client-provided `guest_id` as the quota key.

Create a reusable FastAPI dependency that validates the existing JWT and returns an actor (registered user or guest). Put it in `app/api/dependencies.py`:

```python
from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Actor:
    kind: str  # "user" or "guest"
    id: str


def current_actor(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Actor:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("token_type") == "guest":
            guest_id = payload.get("guest_id")
            if isinstance(guest_id, str) and guest_id:
                return Actor(kind="guest", id=guest_id)
        user_id = payload.get("user_id")
        if isinstance(user_id, int):
            return Actor(kind="user", id=str(user_id))
        raise ValueError("invalid token subject")
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
```

Create a guest session using a cryptographically random ID (`secrets.token_urlsafe`), with claims such as `token_type: "guest"`, `guest_id`, `iat`, `exp`, and `jti`. Give it a short expiration (for example, 24 hours) and **never** give it user-account privileges. Add optional `issuer` and `audience` claims if the token will be used beyond this service.

Store each guest session/server-side quota record in Redis or the database. A record should contain the random guest ID, expiration, usage counters, and a hashed device-installation identifier if your privacy policy permits it. A server-side revocation/usage record prevents a stolen or abused token from being usable indefinitely.

Then require an actor in `app/api/routes/chat.py`. Do not trust a user ID or guest ID sent in request JSON.

```python
from fastapi import APIRouter, Depends, status

from app.api.dependencies import Actor, current_actor


@router.post("/completions", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    actor: Actor = Depends(current_actor),
) -> ChatResponse:
    # Check the matching user or guest quota before calling the AI provider.
    # Use actor.kind + actor.id for privacy-safe security logs.
    ...
```

The generated OpenAPI page should now show the bearer lock for chat. Test both paths:

```bash
curl -i -X POST "https://YOUR_DOMAIN/chat/completions" \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello","config":{}}'
# Expected: 401

curl -i -X POST "https://YOUR_DOMAIN/auth/guest-session" \
  -H 'Content-Type: application/json' \
  -d '{}'
# Expected: 201 containing a short-lived guest access token

curl -i -X POST "https://YOUR_DOMAIN/chat/completions" \
  -H 'Authorization: Bearer YOUR_GUEST_OR_USER_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello","config":{}}'
# Expected: 200 while the guest/user is within its quota
```

**Before deploying:** add automated tests for missing, malformed, expired, guest, and registered-user tokens. Test that a guest token cannot call `/users/me` or any account endpoint. Do not log an authorization header or raw JWT.

### 1.2 Do not return internal exceptions to clients

`app/api/routes/chat.py` currently returns `str(e)` for unexpected AI failures. This can reveal provider, configuration, or implementation details.

Replace the last exception response with a generic message while retaining the full exception only in server logs:

```python
except Exception:
    logger.exception("AI request failed")
    return ChatResponse(
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=None,
        error="The chat service is temporarily unavailable",
    )
```

Use parameterized/structured logging if available; never log passwords, tokens, secret values, or full chat text by default.

### 1.3 Limit input and output sizes

Add sensible limits in `app/schema/schemas.py` before a request reaches the model. Initial limits can be conservative and adjusted from real product traffic:

- `message`: maximum 4,000 characters.
- `history`: maximum 20 messages.
- `ChatMessage.content`: maximum 4,000 characters.
- `user_name`: strip whitespace and keep the existing maximum.

Example:

```python
message: str = Field(..., min_length=1, max_length=4000)
history: list[ChatMessage] = Field(default_factory=list, max_length=20)
```

Also set a timeout on the upstream AI call and set Cloud Run maximum instances to a cost ceiling that the team has agreed on. A maximum instance limit is a safety brake, not a substitute for rate limiting.

### 1.4 Turn off public API documentation in production

FastAPI defaults to publishing `/docs`, `/redoc`, and `/openapi.json`. They do not expose secrets, but they make endpoint discovery easier. Use an environment flag and disable them in production:

```python
# app/main.py
from app.core.config import get_settings

settings = get_settings()
is_production = settings.environment == "production"
app = FastAPI(
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)
```

Add `environment: str = "development"` to `Settings`, set `ENVIRONMENT=production` only in the production Cloud Run service, and confirm a production request to `/docs` returns `404`.

## Phase 2 — application abuse controls (this week)

### 2.1 Implement quotas that survive multiple Cloud Run instances

Do not use an in-memory Python dictionary for production rate limits: Cloud Run can run several instances and each has its own memory. Use Redis/Memorystore or the production database with atomic updates.

Start with these product decisions, documented in code/configuration rather than hard-coded magic numbers:

| Endpoint | Suggested starting control | Key |
| --- | --- | --- |
| `POST /auth/login` | 5 failed attempts per account per 15 minutes; short progressive delay | normalized email **and** source IP |
| `POST /auth/register` | 3–10 attempts per IP/hour; require verified email before expensive use | IP/device signal |
| `POST /chat/completions` | lower free guest request/token budget; higher registered-user budget; concurrent request cap | server-issued guest ID or authenticated user ID, plus IP fallback |

Return `429 Too Many Requests` with `Retry-After` where possible. Avoid a permanent account lockout: attackers can use it to lock out real users. Use generic invalid-login responses so attackers cannot enumerate registered emails.

### 2.2 Add a simple quota table and service

For chat, record at least `actor_kind` (`guest` or `user`), actor ID, time window, request count, estimated input/output tokens, and an atomic quota check. Make this check **before** calling the AI provider. Guest limits should be deliberately low (for example, a small number of chats/day) and set from your cost model; registered users can receive a different free or paid allowance. Decide what happens on a quota-store failure (deny, retry once, and alert) rather than allowing quota failures to fail open.

Add tests for: guest quota allows the first request; guest quota returns `429`; registered-user quota is independent; a second concurrent request cannot exceed the limit; and a request without a session/user token is rejected before it reaches the provider.

### 2.3 Improve registration and account security

1. Keep bcrypt (already used) or migrate deliberately to Argon2id; never implement custom password hashing.
2. Add password reset and email verification with single-use, short-lived tokens.
3. Add MFA for admin/support accounts first; consider it for users based on risk and product needs.
4. Introduce CAPTCHA or mobile attestation only after suspicious repeated behavior, not on every successful user action.
5. Validate JWT expiry and algorithm explicitly (the dependency above does this); later add issuer/audience claims if tokens are used by more than this one service.

## Phase 3 — Cloud Run and Google Cloud configuration (this week)

### 3.1 Use a dedicated runtime service account

Do not run production on the default Compute Engine service account.

```bash
gcloud iam service-accounts create ai-companion-run \
  --project="$PROJECT_ID" \
  --display-name="AI Companion Cloud Run runtime"

export RUN_SA="ai-companion-run@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud run services update "$SERVICE" \
  --region="$REGION" \
  --service-account="$RUN_SA"
```

Grant only the exact permissions it needs. For example, grant `roles/secretmanager.secretAccessor` on each individual Secret Manager secret, not at the whole-project level. If using Cloud SQL, grant only the Cloud SQL client permission and use the supported Cloud SQL connection method.

### 3.2 Keep secrets in Secret Manager

Confirm that production secrets are supplied using `--set-secrets`, not committed in `app/.env`, Docker image layers, GitHub Actions variables, or plain Cloud Run environment values. The existing deployment guide is [cloud-run-deployment-canvas.md](cloud-run-deployment-canvas.md).

Search safely for accidental tracked secret files before each release:

```bash
git ls-files | rg '(^|/)(\.env|.*\.pem|.*\.key)$'
git log --all -- app/.env .env
```

If a real secret was ever committed, rotate it; removing the file from the latest commit does not remove it from Git history or prior builds.

### 3.3 Set cost and availability guardrails

In the Cloud Run service configuration:

1. Set a maximum number of instances based on the maximum spend/traffic you can safely tolerate.
2. Set a request timeout appropriate to the AI response time; do not leave long-running requests unlimited by design.
3. Set concurrency only after load testing. A low concurrency reduces per-instance overload but may create more instances; a high value can cause noisy-neighbor delays.
4. Add Cloud Billing budget alerts and Cloud Monitoring alerts for 5xx, instance count, request count, and AI provider usage.

## Phase 4 — put Cloud Armor in front of Cloud Run (planned rollout)

Cloud Armor does not attach directly to a public Cloud Run URL. The standard arrangement is:

```mermaid
flowchart LR
  M["iOS / Android app"] --> LB["External HTTPS Load Balancer"]
  LB --> CA["Cloud Armor policy"]
  CA --> CR["Cloud Run service"]
  CR --> DB["Database and AI provider"]
```

### 4.1 Build and test the edge path

1. Create a global external HTTPS Application Load Balancer with a serverless NEG that points at this Cloud Run service.
2. Attach the custom domain and managed TLS certificate to the load balancer.
3. Confirm health, login, authenticated chat, and error behavior through the custom domain.
4. Change Cloud Run ingress to **Internal and Cloud Load Balancing**.
5. Confirm the custom domain works and a direct `run.app` request is rejected.

Do this in a staging project first. Keep a tested rollback plan: revert ingress only if the load balancer path is unavailable.

### 4.2 Create Cloud Armor rules in preview mode first

Attach a Cloud Armor policy to the load balancer backend. Initially enable preview mode and inspect logs before enforcing blocks.

Suggested priority order:

1. Allow required health-check traffic, if applicable.
2. Rate-limit `POST /auth/login`, `POST /auth/register`, and `POST /chat/completions` by client IP. Use `429` for excess traffic.
3. Add a temporary rate-based ban for clients that repeatedly exceed the threshold.
4. Add preconfigured WAF rules in preview; enforce only rules that do not block valid app traffic.
5. Keep the default allow rule for the public API after application authentication and rate limits are working.

Do not use IP allowlists as the primary mobile-app control: real users move between carrier/Wi-Fi networks and share NAT addresses. Do not treat Cloud Armor IP limits as a replacement for per-account chat quotas.

## Phase 5 — ongoing security practices

### Every release

- Run unit/integration tests for authorization, quota enforcement, and invalid input.
- Check dependency and container image vulnerabilities; update base images and dependencies on a regular schedule.
- Check that production debug/docs routes remain disabled.
- Verify no secret is in the diff, CI log, or image configuration.
- Deploy to staging, test mobile login/chat, then release gradually and watch errors and spend.

### Every month

- Review top endpoints, 401/403/429/5xx rates, Cloud Armor actions, and AI cost by user/endpoint.
- Review service-account IAM permissions and Secret Manager access.
- Restore-test database backups and validate the incident contact/runbook.
- Patch high-severity dependencies and rebuild images.

### Every quarter

- Run an API-focused penetration test or structured security review.
- Exercise a credential-leak and AI-cost-abuse incident simulation.
- Reassess quotas, Cloud Run limits, and Cloud Armor rules using real traffic.

## Definition of done

The first hardening milestone is complete when all statements below are true:

- [ ] A new guest can obtain a short-lived guest-session token and use chat within its small documented free quota.
- [ ] `/chat/completions` without a guest-session or user token receives `401` and never calls the AI provider.
- [ ] Guest and registered users have documented quotas; excess receives `429` before the AI provider is called.
- [ ] Guest tokens cannot access account-specific endpoints.
- [ ] Passwords, JWTs, database URLs, AI keys, and prompts are absent from normal application logs.
- [ ] Production `/docs`, `/redoc`, and `/openapi.json` return `404` (or are intentionally access-controlled).
- [ ] Secrets are Secret Manager references and the Cloud Run runtime account has only required permissions.
- [ ] Cloud Run has documented max-instance and timeout settings plus budget/error alerts.
- [ ] The custom domain uses the load balancer + Cloud Armor path, Cloud Armor rules have been safely enforced, and direct Cloud Run ingress is restricted.
