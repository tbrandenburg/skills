# Garmin Connect Auth Troubleshooting

## Package Setup

The reusable auth package lives at `~/.garmin/`:

```
~/.garmin/
├── pyproject.toml
├── garmin_client/
│   ├── __init__.py
│   └── auth.py
└── tokens.json          ← cached DI Bearer tokens
```

Install into any project venv:

```bash
pip install -e ~/.garmin
```

Usage:

```python
from garmin_client import get_client

client = get_client()          # loads ~/.garmin/tokens.json, or auths from env vars
stats = client.get_stats("2026-04-12")
```

Environment variables:

| Variable | Required | Default |
|---|---|---|
| `GARMIN_CONNECT_USER` | First auth only | — |
| `GARMIN_CONNECT_PASSWORD` | First auth only | — |
| `GARMIN_TOKEN_PATH` | No | `~/.garmin/tokens.json` |

---

## Token Lifecycle

| Token | TTL | Notes |
|---|---|---|
| DI access token (JWT) | ~28 hours | Auto-refreshed by library 15 min before expiry; new token written back to `tokens.json` automatically |
| DI refresh token (opaque UUID) | No expiry field | Used to mint new access tokens. Invalidated only by: Garmin "sign out all devices", password change, or account suspension |

**In normal operation re-auth is almost never needed.** The library silently refreshes the access token in the background on every API call where the token is within 15 minutes of expiry.

---

## Library Bug: Default Login Fails with 429

**Symptom:** `Garmin.login()` always returns 429 or 403 before any credentials are even submitted.

**Root cause:** `garminconnect/client.py:479` uses `impersonate="safari"`. Cloudflare blocks the Safari TLS fingerprint with HTTP 429.

**The library's 4-strategy login order and outcome:**

| Strategy | Endpoint | Result |
|---|---|---|
| `portal+cffi` | `/portal/api/login` | 429 — Cloudflare blocks safari/chrome fingerprints |
| `portal+requests` | `/portal/api/login` | 403 — no TLS impersonation |
| `mobile+cffi` | `/mobile/api/login` | 429 — bug: uses `impersonate="safari"` |
| `mobile+requests` | `/mobile/api/login` | 429 — no TLS impersonation |

**Fix:** The `garmin_client` package bypasses `login()` entirely. It performs the mobile SSO flow directly with `impersonate="chrome110"`, which works. Do not call `client.login()` — use `get_client()` instead.

If you want to patch the library directly:
```bash
sed -i 's/impersonate="safari"/impersonate="chrome110"/' \
  .venv/lib/python3.*/site-packages/garminconnect/client.py
```

---

## Rate Limiting (429 on Credentials)

**Symptom:** Even with `chrome110`, the credential POST returns 429.

**Root cause:** Garmin rate-limits failed or repeated auth attempts **per account credential**, not per IP, client ID, or endpoint.

**Key findings (verified 2026-04-11):**

- All three endpoints (`/sso/signin`, `/mobile/api/login`, `/portal/api/login`) return 429 simultaneously when rate-limited.
- Rate-limit window: ~1 hour for light abuse; can extend to 24+ hours with many rapid attempts.
- The "widget flow" (`/sso/embed` without `clientId`, proposed in upstream PR #345) also returns 429 at the same time — it does **not** bypass the rate limit. PR #345's premise is incorrect.

**Recovery:**
- Wait. The rate limit clears on its own (1–24h depending on volume of attempts).
- Do not retry during the wait — each retry resets the window.

**Prevention:**
- Token caching is the only reliable mitigation. With `~/.garmin/tokens.json` in place, re-auth happens at most once per ~28 hours (access token TTL). In practice almost never, because the refresh token is long-lived.
- Never call `get_client()` in a tight loop or without checking for a cached token first.

---

## Browser Session Cookies (Dead End)

**Symptom:** You have valid `session`, `JWT_WEB`, `SESSIONID` cookies from a logged-in browser but API calls return 403.

**Root cause:** The `session` cookie is an Iron-signed `Fe26.2` token. It is **IP-bound** (and likely TLS-session-bound to the originating browser). It cannot be reused from a different host/IP regardless of TLS impersonation used.

**All impersonations tested and confirmed failing:** `firefox`, `firefox135`, `firefox133`, `chrome`, `chrome120`, `edge101`.

**Conclusion:** Do not attempt browser cookie extraction. Use `get_client()` with the token cache.

---

## Diagnosing a 403 on API Calls (Post-Auth)

If `get_client()` succeeds but API calls return 403:

1. **`display_name` not set** — `get_stats()` and several other methods require `client.display_name`. The `garmin_client` package fetches this automatically via `socialProfile`. If you construct a `Garmin()` instance manually, fetch it yourself:
   ```python
   prof = client.client.connectapi("/userprofile-service/socialProfile")
   client.display_name = prof.get("displayName", "")
   ```

2. **Stale access token not refreshed** — If the token file was loaded outside the library (e.g. manually copied), call `client.client._token_expires_soon()` to check and `client.client._refresh_di_token()` to force refresh.

3. **Token file corrupted** — Delete `~/.garmin/tokens.json` and re-auth from credentials.

---

## Diagnosing a `BackendUnavailable` pip Install Error

**Symptom:** `pip install -e ~/.garmin` fails with `ModuleNotFoundError: No module named 'setuptools.backends'`.

**Root cause:** Old system Python is used as the build backend; its setuptools predates `setuptools.backends`.

**Fix:** `pyproject.toml` must use `build-backend = "setuptools.build_meta"` (not `setuptools.backends.legacy:build`). The `~/.garmin/pyproject.toml` already has the correct value.
