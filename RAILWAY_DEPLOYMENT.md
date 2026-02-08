# Railway Backend Deployment Guide

**Backend Stack**: FastAPI + PostgreSQL (Neon) + Redis
**Date**: 2026-02-08
**Status**: Ready to deploy ✅

---

## Prerequisites

- Railway account (free tier available)
- GitHub account
- OpenAI API key (for AI features)
- Google OAuth credentials (optional - can skip for now)

---

## Deployment Options

### Option 1: Deploy via Railway Dashboard (Recommended)

#### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Authorize Railway to access your GitHub
6. Select repository: `404mw/TODO-GIAIC`
7. Select branch: `003-perpetua-backend` (backend-only branch)

#### Step 2: Configure Build Settings

Railway will auto-detect the Dockerfile. Verify:

```
Build:
  - Builder: Dockerfile
  - Dockerfile Path: backend/Dockerfile
  - Root Directory: backend/

Deploy:
  - Start Command: alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 4
  - Health Check Path: /health/live
```

#### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will provision a PostgreSQL instance
4. Copy the connection string (DATABASE_URL)

**Alternative: Use Neon Serverless Postgres** (Recommended)
- Go to [neon.tech](https://neon.tech)
- Create free account
- Create new project
- Copy connection string (make sure it uses `postgresql+asyncpg://`)

#### Step 4: Generate JWT Keys

Run locally to generate keys:

```bash
# Generate RSA key pair
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# View private key (copy entire output including BEGIN/END lines)
cat private.pem

# View public key
cat public.pem
```

#### Step 5: Set Environment Variables

In Railway project → **Variables** tab, add:

**REQUIRED (Minimum for deployment):**

```env
# Database (use Railway PostgreSQL or Neon)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require

# JWT Keys (paste entire key including BEGIN/END lines)
JWT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
...entire private key...
-----END PRIVATE KEY-----

JWT_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvXxZ...
...entire public key...
-----END PUBLIC KEY-----

JWT_ALGORITHM=RS256
JWT_ACCESS_EXPIRY_MINUTES=15
JWT_REFRESH_EXPIRY_DAYS=7

# OpenAI (for AI features)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4-turbo

# Application Settings
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-frontend.vercel.app"]
API_BASE_URL=${{RAILWAY_PUBLIC_DOMAIN}}
```

**OPTIONAL (can add later):**

```env
# Google OAuth (optional - can skip)
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret

# Deepgram Voice (optional)
DEEPGRAM_API_KEY=your-key

# WebPush Notifications (optional)
VAPID_PRIVATE_KEY=...
VAPID_CONTACT_EMAIL=admin@yourapp.com

# Payment Processing (optional)
CHECKOUT_SECRET_KEY=sk_...
CHECKOUT_WEBHOOK_SECRET=whsec_...

# Rate Limits (defaults are fine)
RATE_LIMIT_GENERAL=100
RATE_LIMIT_AI=20
RATE_LIMIT_AUTH=10

# Feature Flags
ENABLE_VOICE_TRANSCRIPTION=true
```

**IMPORTANT**:
- For `DATABASE_URL`, ensure it uses `postgresql+asyncpg://` (not `postgres://` or `postgresql://`)
- For JWT keys, paste the ENTIRE key including the `-----BEGIN...-----` and `-----END...-----` lines
- For `CORS_ORIGINS`, use JSON array format: `["https://domain1.com","https://domain2.com"]`

#### Step 6: Deploy

1. Click **"Deploy"** in Railway dashboard
2. Railway will:
   - Build the Docker image
   - Run database migrations (`alembic upgrade head`)
   - Start the application
3. Monitor deployment logs for errors

#### Step 7: Verify Deployment

Once deployed, you'll get a URL like: `https://your-app.up.railway.app`

Test endpoints:

```bash
# Health check
curl https://your-app.up.railway.app/health/live

# Expected response:
# {"status":"healthy","timestamp":"2026-02-08T..."}

# API docs
# Visit: https://your-app.up.railway.app/docs
```

---

### Option 2: Deploy via Railway CLI

#### Step 1: Install Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Or via npm
npm install -g @railway/cli
```

#### Step 2: Login

```bash
railway login
```

#### Step 3: Initialize Project

```bash
cd backend
railway init
```

Select:
- Create new project: `perpetua-backend`
- Link to GitHub repo: `404mw/TODO-GIAIC`

#### Step 4: Add Database

```bash
railway add postgresql
```

Or use Neon and manually set DATABASE_URL.

#### Step 5: Set Environment Variables

```bash
# Set variables one by one
railway variables set DATABASE_URL="postgresql+asyncpg://..."
railway variables set JWT_PRIVATE_KEY="$(cat private.pem)"
railway variables set JWT_PUBLIC_KEY="$(cat public.pem)"
railway variables set OPENAI_API_KEY="sk-..."
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"
railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app"]'

# Or use a file
railway variables set --from-file .env.production
```

#### Step 6: Deploy

```bash
railway up
```

#### Step 7: Get Deployment URL

```bash
railway domain
```

---

## Environment Variables Reference

### Essential (Required)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host/db` |
| `JWT_PRIVATE_KEY` | RSA private key for JWT signing | `-----BEGIN PRIVATE KEY-----\n...` |
| `JWT_PUBLIC_KEY` | RSA public key for JWT verification | `-----BEGIN PUBLIC KEY-----\n...` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-proj-...` |
| `CORS_ORIGINS` | Allowed frontend origins (JSON array) | `["https://app.vercel.app"]` |

### Optional (Can skip initially)

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | None (OAuth disabled) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | None |
| `DEEPGRAM_API_KEY` | Voice transcription API key | None (voice disabled) |
| `RATE_LIMIT_GENERAL` | General API rate limit (req/min) | 100 |
| `RATE_LIMIT_AI` | AI endpoint rate limit | 20 |
| `DEBUG` | Enable debug mode | false |
| `ENVIRONMENT` | Deployment environment | production |

### Computed (Auto-set by Railway)

| Variable | Description |
|----------|-------------|
| `PORT` | Application port (Railway sets this) |
| `RAILWAY_PUBLIC_DOMAIN` | Your app's public URL |

---

## Post-Deployment

### 1. Test API Endpoints

```bash
# Health check
curl https://your-app.up.railway.app/health/live

# Register a test user
curl -X POST https://your-app.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Login
curl -X POST https://your-app.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### 2. Update Frontend Environment

Once backend is deployed, update frontend with:

```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app/api/v1
```

### 3. Update CORS Origins

In Railway, update `CORS_ORIGINS` to include your Vercel frontend URL:

```env
CORS_ORIGINS=["https://your-app.vercel.app","http://localhost:3000"]
```

---

## Monitoring & Logs

### View Logs (Dashboard)
1. Go to Railway project
2. Click on your service
3. Click **"Deployments"** → Select active deployment → **"View Logs"**

### View Logs (CLI)
```bash
railway logs
```

### Metrics
Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Response times

Access via: Project → Service → **Metrics** tab

---

## Database Migrations

Migrations run automatically on deployment via the start command:
```bash
alembic upgrade head && uvicorn src.main:app...
```

### Manual Migration (if needed)

```bash
# SSH into Railway container
railway run bash

# Run migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## Troubleshooting

### Build Fails

**Issue**: Dockerfile build errors

**Solutions**:
- Check Railway build logs
- Verify `backend/pyproject.toml` has all dependencies
- Ensure Dockerfile path is correct: `backend/Dockerfile`

### Database Connection Fails

**Issue**: `could not connect to server`

**Solutions**:
- Verify `DATABASE_URL` format: `postgresql+asyncpg://...`
- Ensure `?sslmode=require` is appended for Neon/external DBs
- Check database is running (Railway PostgreSQL or Neon)

### JWT Errors

**Issue**: `Invalid token` or `Could not validate credentials`

**Solutions**:
- Verify `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY` are complete
- Include `-----BEGIN...-----` and `-----END...-----` markers
- Ensure no extra whitespace or line breaks
- Check `JWT_ALGORITHM=RS256`

### CORS Errors

**Issue**: `CORS policy blocked`

**Solutions**:
- Add frontend URL to `CORS_ORIGINS`
- Use JSON array format: `["https://app.vercel.app"]`
- Include both production and localhost URLs for testing

### OpenAI API Errors

**Issue**: `Insufficient quota` or `Invalid API key`

**Solutions**:
- Verify `OPENAI_API_KEY` is valid
- Check OpenAI account has credits
- AI features will gracefully degrade if API fails

---

## Cost Estimates

### Railway (Free Tier)
- **Included**: $5/month in usage credits
- **Web Service**: ~$5/month (512MB RAM, 1 vCPU)
- **PostgreSQL**: ~$5/month (if using Railway DB)

**Total**: Can run on free tier with light usage

### External Services
- **Neon PostgreSQL**: Free tier available (0.5GB storage)
- **OpenAI API**: Pay-per-use (~$0.002 per request)
- **Deepgram**: Free tier 45,000 minutes/month

---

## Scaling Considerations

### Horizontal Scaling (Traffic)
Railway auto-scales based on:
- CPU usage
- Memory usage
- Request volume

Configure in: **Settings** → **Scaling**

### Database Scaling
- **Neon**: Supports auto-scaling, branching
- **Railway PostgreSQL**: Manual scaling via dashboard

### Workers
Start command uses 4 workers:
```bash
uvicorn src.main:app --workers 4
```

Adjust based on traffic:
- Light: 2 workers
- Medium: 4 workers (current)
- Heavy: 8+ workers

---

## Security Checklist

- [x] `DEBUG=false` in production
- [x] `ENVIRONMENT=production`
- [x] Strong JWT keys (2048-bit RSA)
- [x] CORS restricted to frontend domains only
- [x] Database uses SSL (`sslmode=require`)
- [x] Rate limiting enabled
- [ ] Custom domain with HTTPS (optional)
- [ ] Environment variables not committed to git
- [ ] Regular security updates

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Get deployment URL
3. 🔜 Test API endpoints
4. 🔜 Update frontend `.env.local` with backend URL
5. 🔜 Recreate `frontend/src/lib/` directory
6. 🔜 Deploy frontend to Vercel
7. 🔜 Update `CORS_ORIGINS` with frontend URL

---

## Quick Reference

**Railway Dashboard**: https://railway.app/dashboard
**API Docs**: https://your-app.up.railway.app/docs
**Health Check**: https://your-app.up.railway.app/health/live
**OpenAPI Spec**: https://your-app.up.railway.app/openapi.json

---

**Ready to deploy!** Follow Option 1 (Dashboard) for the easiest experience.
