"""
NutriLens Backend - Rate Limiter

Simple in-memory rate limiting for auth endpoints.
"""

import time
from collections import defaultdict
from typing import Optional
from dataclasses import dataclass, field

from fastapi import Request, HTTPException, status


@dataclass
class RateLimitEntry:
    """Rate limit tracking entry."""
    count: int = 0
    window_start: float = field(default_factory=time.time)


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter.
    
    Note: This is suitable for single-instance deployments.
    For production with multiple instances, use Redis-based limiting.
    """
    
    def __init__(self):
        self._store: dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
    
    def _get_key(self, request: Request, key_prefix: str) -> str:
        """Generate rate limit key from request."""
        # Use client IP as identifier
        client_ip = request.client.host if request.client else "unknown"
        return f"{key_prefix}:{client_ip}"
    
    def check_rate_limit(
        self,
        request: Request,
        key_prefix: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, Optional[int]]:
        """
        Check if request is within rate limits.
        
        Returns:
            (is_allowed, retry_after_seconds)
        """
        key = self._get_key(request, key_prefix)
        now = time.time()
        
        entry = self._store[key]
        
        # Reset window if expired
        if now - entry.window_start >= window_seconds:
            entry.count = 0
            entry.window_start = now
        
        # Check limit
        if entry.count >= max_requests:
            retry_after = int(window_seconds - (now - entry.window_start))
            return False, max(1, retry_after)
        
        # Increment count
        entry.count += 1
        return True, None
    
    def reset(self, request: Request, key_prefix: str) -> None:
        """Reset rate limit for a key."""
        key = self._get_key(request, key_prefix)
        if key in self._store:
            del self._store[key]


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def check_login_rate_limit(request: Request) -> None:
    """Check login rate limit - 5 attempts per minute."""
    allowed, retry_after = rate_limiter.check_rate_limit(
        request,
        key_prefix="login",
        max_requests=5,
        window_seconds=60,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )


def check_forgot_password_rate_limit(request: Request) -> None:
    """Check forgot password rate limit - 3 attempts per 10 minutes."""
    allowed, retry_after = rate_limiter.check_rate_limit(
        request,
        key_prefix="forgot_password",
        max_requests=3,
        window_seconds=600,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many password reset attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )
