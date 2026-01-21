# Authentication & Authorization

**Feature**: Perpetua Flow Backend API
**Date**: 2026-01-19
**Status**: Draft

## Overview

Perpetua Flow uses Google OAuth 2.0 for user authentication, with JWT tokens for API authorization. The frontend uses BetterAuth to handle the OAuth UI flow, while the backend validates tokens and manages sessions.

---

## Authentication Flow

### 1. Google OAuth Flow

```
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│  User   │         │Frontend │         │ Backend │         │ Google  │
│         │         │BetterAuth│        │   API   │         │  OAuth  │
└────┬────┘         └────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │                   │
     │ Click "Sign In"   │                   │                   │
     │──────────────────>│                   │                   │
     │                   │                   │                   │
     │                   │ Redirect to Google Auth              │
     │                   │──────────────────────────────────────>│
     │                   │                   │                   │
     │                   │                   │    Authorization  │
     │<──────────────────────────────────────────────────────────│
     │                   │                   │     Screen        │
     │                   │                   │                   │
     │ Grant Permission  │                   │                   │
     │──────────────────────────────────────────────────────────>│
     │                   │                   │                   │
     │                   │   Redirect with Authorization Code   │
     │                   │<─────────────────────────────────────│
     │                   │                   │                   │
     │                   │ POST /auth/google/callback           │
     │                   │ { code: "..." }   │                   │
     │                   │──────────────────>│                   │
     │                   │                   │                   │
     │                   │                   │ Exchange code     │
     │                   │                   │──────────────────>│
     │                   │                   │                   │
     │                   │                   │ Google ID Token   │
     │                   │                   │<─────────────────│
     │                   │                   │                   │
     │                   │                   │ Verify & Create   │
     │                   │                   │ User (if new)     │
     │                   │                   │                   │
     │                   │ { access_token, refresh_token }      │
     │                   │<─────────────────│                   │
     │                   │                   │                   │
     │  Redirect to App  │                   │                   │
     │<─────────────────│                   │                   │
     │                   │                   │                   │
```

### 2. Token Types

#### Access Token (JWT)

- **Purpose**: Authorize API requests
- **Expiry**: 15 minutes
- **Storage**: Memory only (frontend)
- **Algorithm**: RS256 (RSA + SHA-256)

**JWT Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "tier": "pro",
  "iat": 1705671000,
  "exp": 1705671900,
  "iss": "perpetua-flow",
  "aud": "perpetua-flow-api"
}
```

**JWT Header**:
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-2026-01"
}
```

#### Refresh Token

- **Purpose**: Obtain new access tokens
- **Expiry**: 7 days
- **Storage**: HttpOnly cookie (secure, same-site)
- **Rotation**: New refresh token issued on each use

---

## Token Management

### Token Refresh Flow

```
┌─────────┐         ┌─────────┐
│Frontend │         │ Backend │
└────┬────┘         └────┬────┘
     │                   │
     │ API Request       │
     │ (expired token)   │
     │──────────────────>│
     │                   │
     │ 401 UNAUTHORIZED  │
     │ { refresh_required: true }
     │<─────────────────│
     │                   │
     │ POST /auth/refresh│
     │ { refresh_token } │
     │──────────────────>│
     │                   │
     │ { new_access_token,│
     │   new_refresh_token }
     │<─────────────────│
     │                   │
     │ Retry original    │
     │ request           │
     │──────────────────>│
     │                   │
```

### Token Storage Best Practices

| Token Type | Storage Location | Security Measures |
|------------|------------------|-------------------|
| Access Token | Memory (JS variable) | Never in localStorage/sessionStorage |
| Refresh Token | HttpOnly Cookie | Secure, SameSite=Strict, Path=/api/v1/auth |

### Token Refresh Strategy (Frontend)

```typescript
// Pseudo-code for token refresh
class TokenManager {
  private accessToken: string | null = null;
  private refreshPromise: Promise<string> | null = null;

  async getAccessToken(): Promise<string> {
    if (this.accessToken && !this.isExpired(this.accessToken)) {
      return this.accessToken;
    }

    // Prevent multiple simultaneous refresh requests
    if (!this.refreshPromise) {
      this.refreshPromise = this.refreshToken();
    }

    return this.refreshPromise;
  }

  private async refreshToken(): Promise<string> {
    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include' // Include HttpOnly cookie
      });

      if (!response.ok) {
        throw new AuthenticationError('Refresh failed');
      }

      const { access_token } = await response.json();
      this.accessToken = access_token;
      return access_token;
    } finally {
      this.refreshPromise = null;
    }
  }
}
```

---

## Authorization

### Role-Based Access Control

Perpetua Flow uses a simple tier-based authorization model:

| Tier | Access Level |
|------|--------------|
| `free` | Basic features, limited quotas |
| `pro` | All features, expanded quotas |

### Resource Ownership

All user resources are strictly owned:

```python
# Backend authorization check
def authorize_resource_access(user_id: UUID, resource: Resource) -> bool:
    if resource.user_id != user_id:
        raise ForbiddenError("Access denied to resource")
    return True
```

### Cross-User Access Prevention

- **FR-005**: System MUST return 403 FORBIDDEN for cross-user resource access attempts
- All API endpoints validate `user_id` from JWT matches resource owner
- No admin roles or shared resources in v1

---

## Security Measures

### 1. Token Security

| Measure | Implementation |
|---------|----------------|
| Short-lived access tokens | 15-minute expiry |
| Refresh token rotation | New token on each use |
| Secure cookie flags | HttpOnly, Secure, SameSite=Strict |
| JWT signature verification | RS256 with rotating keys |
| Token revocation | Logout invalidates refresh token |

### 2. API Security

| Measure | Implementation |
|---------|----------------|
| HTTPS only | All traffic encrypted |
| CORS | Strict origin validation |
| Rate limiting | Per-user and per-IP limits |
| Request validation | Zod/Pydantic schema validation |
| Idempotency keys | Prevent duplicate mutations |

### 3. OAuth Security

| Measure | Implementation |
|---------|----------------|
| State parameter | CSRF protection in OAuth flow |
| PKCE | Proof Key for Code Exchange |
| Token binding | Validate redirect URI |
| Scope limitation | Only request needed scopes |

---

## JWT Key Management

### Key Rotation

```python
# Key rotation schedule
KEY_ROTATION_INTERVAL = timedelta(days=30)
KEY_OVERLAP_PERIOD = timedelta(days=7)

class JWTKeyManager:
    def __init__(self):
        self.current_key: RSAPrivateKey
        self.previous_key: RSAPrivateKey | None
        self.current_kid: str
        self.previous_kid: str | None

    def sign_token(self, payload: dict) -> str:
        """Always sign with current key"""
        return jwt.encode(
            payload,
            self.current_key,
            algorithm="RS256",
            headers={"kid": self.current_kid}
        )

    def verify_token(self, token: str) -> dict:
        """Accept current and previous key during overlap"""
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        if kid == self.current_kid:
            key = self.current_key.public_key()
        elif kid == self.previous_kid:
            key = self.previous_key.public_key()
        else:
            raise InvalidTokenError("Unknown key ID")

        return jwt.decode(token, key, algorithms=["RS256"])
```

### JWKS Endpoint

**Endpoint**: `GET /api/v1/.well-known/jwks.json`

**Response**:
```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "key-2026-01",
      "use": "sig",
      "alg": "RS256",
      "n": "0vx7agoebGcQSuu...",
      "e": "AQAB"
    }
  ]
}
```

---

## Session Management

### Session Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    Session States                        │
└─────────────────────────────────────────────────────────┘

[Login] ─────> [Active] ─────> [Expired]
                  │                │
                  │ (refresh)      │ (re-authenticate)
                  └────────────────┘

                  │ (logout)
                  v
              [Terminated]
```

### Session Storage (Backend)

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    token_hash VARCHAR(64) NOT NULL,  -- SHA-256 hash
    device_info JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,

    INDEX idx_refresh_tokens_user (user_id),
    INDEX idx_refresh_tokens_hash (token_hash)
);
```

### Logout Flow

1. Frontend calls `POST /api/v1/auth/logout` with refresh token
2. Backend marks refresh token as revoked
3. Frontend clears access token from memory
4. Browser clears HttpOnly cookie

---

## Error Responses

### Authentication Errors

#### 401 UNAUTHORIZED

**Missing Token**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

**Invalid Token**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid authentication token"
  }
}
```

**Expired Token** (with refresh hint):
```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Access token expired",
    "refresh_required": true
  }
}
```

#### 403 FORBIDDEN

**Cross-User Access**:
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Access denied to resource",
    "resource_id": "550e8400-..."
  }
}
```

**Tier Required**:
```json
{
  "error": {
    "code": "TIER_REQUIRED",
    "message": "This feature requires Pro subscription",
    "required_tier": "pro",
    "current_tier": "free"
  }
}
```

---

## Google OAuth Configuration

### Required Scopes

| Scope | Purpose |
|-------|---------|
| `openid` | OpenID Connect authentication |
| `email` | User email address |
| `profile` | User name and avatar |

### OAuth Credentials

Environment variables (never committed):

```bash
# .env (local development)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# Production
GOOGLE_REDIRECT_URI=https://app.perpetua.flow/auth/callback
```

### Google Cloud Console Setup

1. Create OAuth 2.0 credentials
2. Configure authorized redirect URIs
3. Enable Google+ API (for profile access)
4. Set up OAuth consent screen

---

## Security Checklist

### Implementation Checklist

- [ ] Access tokens expire in 15 minutes
- [ ] Refresh tokens rotate on use
- [ ] Refresh tokens stored in HttpOnly cookies
- [ ] JWT signed with RS256 algorithm
- [ ] Key rotation implemented
- [ ] CORS configured for allowed origins only
- [ ] Rate limiting on auth endpoints
- [ ] Refresh token revocation on logout
- [ ] Cross-user access validation on all endpoints
- [ ] HTTPS enforced in production

### Penetration Testing Targets

- OAuth state parameter validation
- Token signature verification
- Cross-user resource access
- Refresh token replay attacks
- JWT algorithm confusion attacks
- Cookie security attributes

---

## Monitoring & Alerts

### Auth Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| Login failures/min | > 100 |
| Token refresh rate | Unusual spikes |
| OAuth callback errors | > 5% |
| 401/403 responses | > 10% of requests |

### Audit Logging

All authentication events are logged:

```json
{
  "event": "user_login",
  "user_id": "550e8400-...",
  "timestamp": "2026-01-19T10:00:00.000Z",
  "ip_address": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "result": "success",
  "method": "google_oauth"
}
```

---

## References

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)
- [BetterAuth Documentation](https://better-auth.com)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
