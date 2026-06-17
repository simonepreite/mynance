"""In-memory auth runtime state: a logout denylist and a brute-force limiter.

Process-local and intentionally simple — adequate for the single-instance MVP
deploy (FR-2 logout, Story 1.4 rate limiting). Documented limitation: state is
not shared across processes and resets on restart; a Redis-backed store is the
natural upgrade when the deployment scales horizontally.
"""

import time

# --- logout denylist (revoked token jtis) ---------------------------------
_revoked_jtis: set[str] = set()


def revoke_token(jti: str) -> None:
    _revoked_jtis.add(jti)


def is_token_revoked(jti: str) -> bool:
    return jti in _revoked_jtis


# --- sliding-window rate limiter ------------------------------------------
_attempts: dict[str, list[float]] = {}


def too_many_attempts(
    key: str, *, max_attempts: int = 10, window_seconds: float = 60.0
) -> bool:
    """Record an attempt for ``key``; return True once it exceeds the window."""
    now = time.monotonic()
    recent = [t for t in _attempts.get(key, []) if now - t < window_seconds]
    recent.append(now)
    _attempts[key] = recent
    return len(recent) > max_attempts
