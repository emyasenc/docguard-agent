"""
Security utilities for DocGuard.
Handles webhook verification, API key authentication, and secure token generation.
"""

import hmac
import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException, status, Request

logger = logging.getLogger(__name__)

# ============================================
# WEBHOOK SIGNATURE VERIFICATION
# ============================================

def verify_webhook_signature(
    payload: bytes,
    signature_header: Optional[str],
    secret: str
) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body as bytes
        signature_header: Value of X-Hub-Signature-256 header
        secret: Webhook secret from environment
    
    Returns:
        True if signature is valid, False otherwise
    
    Example:
        >>> verify_webhook_signature(b'{"test": true}', "sha256=abc123...", "my_secret")
        True
    """
    if not secret:
        logger.warning("⚠️ Webhook secret not configured. Skipping verification.")
        return True
    
    if not signature_header:
        logger.warning("⚠️ Missing signature header.")
        return False
    
    # Extract the signature from the header
    if not signature_header.startswith("sha256="):
        logger.warning("⚠️ Invalid signature format.")
        return False
    
    expected_signature = signature_header.replace("sha256=", "")
    
    # Compute HMAC-SHA256
    computed = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(computed, expected_signature)
    
    if not is_valid:
        logger.warning("❌ Invalid webhook signature")
    
    return is_valid

def require_valid_signature(request: Request, secret: str) -> None:
    """
    FastAPI dependency that verifies webhook signature.
    
    Raises HTTPException 401 if signature is invalid.
    
    Args:
        request: FastAPI Request object
        secret: Webhook secret from environment
    
    Raises:
        HTTPException: 401 Unauthorized if signature is invalid
    """
    if not secret:
        logger.info("⚠️ No webhook secret configured. Skipping verification.")
        return
    
    signature_header = request.headers.get("X-Hub-Signature-256")
    
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )
    
    # Get raw payload
    payload = request.body()
    
    # Verify signature
    is_valid = verify_webhook_signature(payload, signature_header, secret)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )


# ============================================
# API KEY AUTHENTICATION (Optional)
# ============================================

def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        A 32-character URL-safe base64 encoded string
    
    Example:
        >>> key = generate_api_key()
        >>> len(key)
        43
    """
    return secrets.token_urlsafe(32)

def verify_api_key(api_key: str, expected_key: Optional[str]) -> bool:
    """
    Verify an API key using constant-time comparison.
    
    Args:
        api_key: The API key to verify
        expected_key: The expected API key from environment
    
    Returns:
        True if keys match, False otherwise
    
    Example:
        >>> verify_api_key("my-key", "my-key")
        True
        >>> verify_api_key("wrong", "my-key")
        False
    """
    if not expected_key:
        # No key configured = allow all requests (development mode)
        return True
    
    return hmac.compare_digest(api_key.encode("utf-8"), expected_key.encode("utf-8"))


# ============================================
# SECURE TOKEN GENERATION
# ============================================

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure token.
    
    Args:
        length: Length of the token in bytes (default: 32)
    
    Returns:
        A URL-safe base64 encoded string
    
    Example:
        >>> token = generate_secure_token()
        >>> len(token) > 30
        True
    """
    return secrets.token_urlsafe(length)

def generate_webhook_secret() -> str:
    """
    Generate a secure webhook secret.
    
    Returns:
        A 32-character URL-safe base64 encoded string
    
    Example:
        >>> secret = generate_webhook_secret()
        >>> len(secret) > 30
        True
    """
    return secrets.token_urlsafe(32)


# ============================================
# RATE LIMITING (Simple In-Memory)
# ============================================

from collections import defaultdict
from time import time
import threading

class SimpleRateLimiter:
    """
    Simple in-memory rate limiter for API endpoints.
    
    Not for production scale—use Redis for production.
    
    Example:
        >>> limiter = SimpleRateLimiter()
        >>> limiter.is_allowed("user_123", limit=10, window=60)
        True
    """
    
    def __init__(self):
        self._requests = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str, limit: int = 10, window: int = 60) -> bool:
        """
        Check if a request is allowed under rate limits.
        
        Args:
            key: Unique identifier (e.g., IP address, API key)
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
        
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = time()
        window_start = now - window
        
        with self._lock:
            # Clean old requests
            self._requests[key] = [
                timestamp for timestamp in self._requests[key]
                if timestamp > window_start
            ]
            
            # Check limit
            if len(self._requests[key]) >= limit:
                return False
            
            # Add current request
            self._requests[key].append(now)
            return True
    
    def get_remaining(self, key: str, limit: int = 10, window: int = 60) -> int:
        """
        Get remaining requests allowed in the current window.
        
        Args:
            key: Unique identifier
            limit: Maximum requests allowed in window
            window: Time window in seconds
        
        Returns:
            Number of remaining requests allowed
        """
        now = time()
        window_start = now - window
        
        with self._lock:
            recent = [
                timestamp for timestamp in self._requests.get(key, [])
                if timestamp > window_start
            ]
            return max(0, limit - len(recent))
    
    def reset(self, key: str) -> None:
        """
        Reset rate limit counter for a key.
        
        Args:
            key: Unique identifier to reset
        """
        with self._lock:
            if key in self._requests:
                del self._requests[key]
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with total keys tracked and total requests
        """
        with self._lock:
            total_requests = sum(len(reqs) for reqs in self._requests.values())
            return {
                "total_keys": len(self._requests),
                "total_requests": total_requests
            }

# ============================================
# DEPENDENCY FOR FASTAPI ROUTES
# ============================================

from fastapi import Depends, Header

def require_api_key(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
    expected_key: Optional[str] = None
) -> str:
    """
    FastAPI dependency that requires a valid API key.
    
    Args:
        api_key: The API key from the request header
        expected_key: The expected API key from environment
    
    Raises:
        HTTPException: 401 if API key is missing or invalid
    
    Returns:
        The API key if valid
    
    Example:
        ```python
        @app.get("/protected")
        def protected_route(api_key: str = Depends(require_api_key)):
            return {"message": "You're authenticated!"}
    """
    if verify_api_key(api_key, expected_key):
            return api_key

    raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or missing API key"
    )
            