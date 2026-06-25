# Design — Email su registrazione + verifica email + reset password

**Date:** 2026-06-25 · **Project:** mynance · **Author:** Simone (+ AI dev)
**Status:** Approved — implementing on branch `feat/story-1-1-scaffold`.

## Goal

On top of the shipped MVP, add an email to the `Utente` domain and build two
email-driven flows:

1. **Email at registration** — registration now requires an email; the account
   starts **unverified** and a verification link is sent.
2. **Email verification (gate)** — login is **blocked until the email is
   verified** (with a resend option).
3. **Password reset via email** — "forgot password" sends a tokenized reset
   link. The existing one-time **recovery-code** flow is **kept as a fallback**.

The send engine (`emails` lib + MJML templates + SMTP config) already exists in
the codebase (template heritage); we reuse it. We do **not** reuse the template's
`User`-based email endpoints — the app's real users are `Utente`. All flows are
built natively on the `Utente` domain under `/api/v1/auth`.

## Decisions (from brainstorming)

- **Login identifier:** username **or** email (lookup resolves either).
- **Pre-verification:** login is **blocked** until verified (403 + resend).
- **Recovery-code:** **kept** as a fallback alongside email reset.
- **Token mechanism:** **single-use, hashed in DB** (revocable, expiring) — not
  stateless JWT. Consistent with the existing `recovery_code_hash` precedent and
  appropriate for a finance app.
- **Provider:** **Brevo** in production (SMTP relay); **dev = log the link to the
  backend console** (no service, sidesteps the corporate proxy).
- **No auto-login after registration** — the user lands on a "verify your email"
  screen.
- **Existing accounts grandfathered** — migration sets `email_verified = True`
  for pre-feature rows (which have no email); they keep logging in by username
  and the recovery-code still works.

## Data model

`Utente` (table `utente`) gains:

- `email: str | None` — **unique**, indexed, `max_length=255`. Nullable only to
  grandfather existing rows; **required for new registrations** (enforced at the
  schema/API boundary, not by DB nullability). Postgres allows multiple `NULL`s
  under a unique constraint, so grandfathered rows coexist.
- `email_verified: bool` — `default=False`, `server_default` false. Migration
  **backfills `True`** on existing rows.

New table `utente_token` (single-use tokens):

- `id: uuid` (pk)
- `utente_id: uuid` — FK → `utente.id`, **indexed**
- `token_hash: str` — only the hash of the random token is stored (same approach
  as `recovery_code_hash`)
- `purpose: str` — `"email_verify"` | `"password_reset"`
- `expires_at: datetime`
- `used_at: datetime | None` — `NULL` = unused; set on consumption (single-use)
- `created_at: datetime`

**Token lifecycle:** issuing a new token of a given `(utente_id, purpose)`
**invalidates** prior unused tokens for that pair (mark them used), so a "resend"
disables the previous links. A token is valid iff `used_at IS NULL` and
`expires_at > now` and `purpose` matches.

**Migration** (new Alembic revision): add `email` + `email_verified` to `utente`
(backfill verified=True), create `utente_token` with its FK + index.

**Config** additions:
- `EMAIL_VERIFY_TOKEN_EXPIRE_HOURS: int = 24`.
- Reuse the existing `EMAIL_RESET_TOKEN_EXPIRE_HOURS = 48` for password reset.

## Schemas

- `UtenteRegister` — gains `email: EmailStr` (required).
- `UtenteLogin` — `username` field becomes `identifier: str` (username **or**
  email). (Client + frontend updated accordingly.)
- `UtentePublic` — gains `email: str | None` and `email_verified: bool`.
- New request schemas:
  - `EmailVerifyRequest { token: str }`
  - `ResendVerificationRequest { identifier: str }`
  - `ForgotPasswordRequest { email: EmailStr }`
  - `ResetPasswordRequest { token: str, new_password: str }` (min length reused
    from the existing password rule).
- New response schema `MessageResponse { message: str }` for the generic flows
  (or reuse the template's `Message` if present).

## API surface (all under `/api/v1/auth`)

- `POST /register` — requires `email`. Creates `Utente` with
  `email_verified=False`; still generates the one-time `recovery_code`
  (returned once, as today); issues an `email_verify` token and sends the
  verification email. **Does not** return a session token. Errors:
  username taken → 409 (existing); **email taken → 409**.
- `POST /login` — body `{identifier, password}`. Resolve `Utente` by username
  **or** email. If password is correct but `email_verified is False` → **403**
  with a distinct error code/detail so the frontend can show "resend". Otherwise
  returns the access token as today. Rate-limited via the existing
  `too_many_attempts`.
- `POST /verify-email` — `{token}`. Consume an `email_verify` token; set
  `email_verified=True`. Invalid/used/expired/wrong-purpose → 400.
- `POST /resend-verification` — `{identifier}`. If the resolved account exists
  and is unverified, invalidate old tokens, issue a new one, send the email.
  **Always responds 200 generically** (no account enumeration). Rate-limited.
- `POST /forgot-password` — `{email}`. If the email maps to an account, issue a
  `password_reset` token and send the email. **Always 200 generically.**
  Rate-limited.
- `POST /reset-password` — `{token, new_password}`. Consume a `password_reset`
  token; set the new `password_hash`. Invalid/used/expired → 400.
- `POST /recover` (username + recovery_code → new password) — **unchanged**,
  remains as the offline fallback.

## Email sending (dev vs prod)

- A small wrapper used by the Utente flows: if `settings.emails_enabled`, call
  the existing `send_email(...)`; otherwise (**dev**) `logger.info(...)` the full
  link. This avoids the template's `assert settings.emails_enabled` in
  `send_email` and lets local dev click the link from the backend logs (no SMTP,
  no corporate-proxy issue).
- Templates: reuse the existing `reset_password` template; **add a `verify_email`
  template** (MJML source under `email-templates/src/` + built HTML under
  `email-templates/build/`, modeled on `new_account`).
- Links target `settings.FRONTEND_HOST` (already configured):
  `${FRONTEND_HOST}/verify-email?token=…` and
  `${FRONTEND_HOST}/reset-password?token=…`.

## Brevo (production)

SMTP only — no provider-specific code. `.env` (added commented to `.env.example`):

```
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=<Brevo login>
SMTP_PASSWORD=<Brevo SMTP key>
EMAILS_FROM_EMAIL=<verified sender>
EMAILS_FROM_NAME=mynance
```

In dev `SMTP_HOST` stays empty → `emails_enabled` false → log-in-console.

## Frontend

- [signup.tsx](frontend/src/routes/signup.tsx): add a required **email** field.
  After a successful register, show the recovery-code screen (as today) **plus**
  a "we sent you a verification email" message — **no auto-login**.
- [login.tsx](frontend/src/routes/login.tsx): identifier field labelled
  "**Username o email**". On a 403-unverified response, show the message and a
  "**Reinvia email di verifica**" button (calls `resend-verification`).
- New routes:
  - `verify-email.tsx` — reads `?token`, calls `verify-email`, shows
    success (→ link to login) or error (+ resend option).
  - `recover-password.tsx` — enter email → `forgot-password` → generic
    "check your inbox" message.
  - `reset-password.tsx` — reads `?token`, new-password form → `reset-password`
    → success → login.
- The existing recovery-code recover page stays as a fallback, linked as "Ho un
  codice di recupero".
- Regenerate the API client (`openapi-ts`) after the backend changes.

## Security / edge cases

- **Existing accounts**: grandfathered (`email_verified=True`, `email` NULL);
  username login + recovery-code keep working.
- **No account enumeration** on `forgot-password` and `resend-verification`
  (generic 200 regardless of existence).
- **Rate limiting** via the existing `too_many_attempts` on login,
  forgot-password, and resend.
- Tokens are single-use, hashed, expiring; re-issuing invalidates prior unused
  tokens for the same `(utente, purpose)`.
- Password validation reuses the existing `UtenteRegister` password rule for
  `reset-password`.
- Email uniqueness enforced (409 on register if taken).

## Out of scope (YAGNI)

- Changing/adding an email to an existing account.
- Email as the sole login identifier (we keep username-or-email).
- 2FA, magic-link login, email change-of-address verification.

## Testing

**Backend**
- Register requires email; duplicate email → 409; creates an unverified account;
  verification email is sent/logged.
- Login blocked when unverified → 403; succeeds after verification; login works
  by **username** and by **email**.
- `verify-email`: valid token verifies; reused token → 400; expired → 400;
  wrong-purpose token → 400.
- `resend-verification`: generic 200; issues a new token and invalidates the old.
- `forgot-password`: generic 200; reset token issued.
- `reset-password`: valid token resets; reused/expired → 400; login works with
  the new password.
- Recovery-code fallback still works.
- Tokens are single-use and scoped per Utente (cross-Utente token → 400/404).

**Frontend**
- `biome ci` + `tsc` + `vite build` green.
- Email field in signup; login with identifier + resend on unverified; the
  verify-email and reset-password routes (happy path + error path).

## Risks / notes

- The migration must backfill `email_verified=True` for existing rows **before**
  the login gate ships, or pre-feature users get locked out. Covered by the
  migration `server_default`/backfill and asserted by a grandfathering test.
- The "resend" must invalidate prior tokens or stale links accumulate; covered by
  the lifecycle test.
- In dev, the verification/reset link is only visible in the backend logs — call
  this out in the dev workflow notes.
