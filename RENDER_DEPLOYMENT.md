# Render Deployment Guide

## Prerequisites

1. Render account: https://render.com (sign up with GitHub)
2. GitHub repo pushed with `003-perpetua-backend` branch
3. Environment variables ready (API keys, JWT keys)

---

## Option A: Deploy with render.yaml (Recommended)

### 1. Push render.yaml to GitHub

```bash
git add render.yaml RENDER_DEPLOYMENT.md
git commit -m "feat: Add Render deployment configuration"
git push
```

### 2. Connect to Render

1. Go to https://dashboard.render.com
2. Click **New → Blueprint**
3. Connect your GitHub repo
4. Select **`003-perpetua-backend`** branch
5. Render will detect `render.yaml` and show:
   - **Web Service**: perpetua-backend
   - **PostgreSQL**: perpetua-db

### 3. Set Environment Variables

In the Render dashboard, add these **Secret Files** or **Environment Variables**:

**Required Variables:**
```env
OPENAI_API_KEY=sk-proj-...
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
DEEPGRAM_API_KEY=your-deepgram-key
```

**JWT Keys** (copy from `backend/.keys/`):
```env
JWT_PRIVATE_KEY=<paste contents of jwt-rs256.key>
JWT_PUBLIC_KEY=<paste contents of jwt-rs256.key.pub>
```

**Note:** For multi-line values (JWT keys), use "Add Secret File" instead:
- Name: `JWT_PRIVATE_KEY`, File: `backend/.keys/jwt-rs256.key`
- Name: `JWT_PUBLIC_KEY`, File: `backend/.keys/jwt-rs256.key.pub`

### 4. Deploy

Click **Apply** → Render will:
- ✅ Create PostgreSQL database
- ✅ Build Docker image
- ✅ Run migrations (via start.sh)
- ✅ Start uvicorn with 4 workers
- ✅ Assign public URL

---

## Option B: Manual Setup (Alternative)

### 1. Create PostgreSQL Database

1. Dashboard → **New → PostgreSQL**
2. Name: `perpetua-db`
3. Database: `perpetua`
4. User: `perpetua`
5. Region: `Oregon` (or closest to you)
6. Plan: **Free** (or Starter for $7/month)
7. Click **Create Database**
8. Copy **Internal Database URL** (starts with `postgresql://`)

### 2. Create Web Service

1. Dashboard → **New → Web Service**
2. Connect GitHub repo
3. Branch: `003-perpetua-backend`
4. Settings:
   - **Name**: `perpetua-backend`
   - **Region**: `Oregon` (same as database)
   - **Branch**: `003-perpetua-backend`
   - **Root Directory**: `.` (leave empty or set to root)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile`
   - **Docker Command**: (leave empty - uses CMD from Dockerfile)
   - **Plan**: `Free` (or Starter for $7/month)

### 3. Add Environment Variables

Click **Environment** tab and add:

```env
# Database (paste from PostgreSQL dashboard)
DATABASE_URL=postgresql://perpetua:password@...render.com/perpetua

# API Keys
OPENAI_API_KEY=sk-proj-...
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
DEEPGRAM_API_KEY=your-deepgram-key

# JWT Keys (use "Add Secret File" for multi-line)
JWT_PRIVATE_KEY=<from backend/.keys/jwt-rs256.key>
JWT_PUBLIC_KEY=<from backend/.keys/jwt-rs256.key.pub>
```

### 4. Configure Health Check

**Settings → Health Check:**
- Path: `/health/live`
- Timeout: `30` seconds (increase from default)
- Interval: `30` seconds

### 5. Deploy

Click **Manual Deploy → Deploy latest commit**

---

## Post-Deployment

### 1. Verify Deployment

Once deployed, you'll get a URL like:
```
https://perpetua-backend.onrender.com
```

**Test the API:**
```bash
curl https://perpetua-backend.onrender.com/health/live
# Should return: {"status":"ok"}

curl https://perpetua-backend.onrender.com/health/ready
# Should return: {"status":"ready","database":"connected",...}
```

### 2. Check Logs

Dashboard → Your Service → **Logs** tab
- Should show: "Application startup complete" (4 times)
- No errors

### 3. View Database

Dashboard → PostgreSQL Database → **Info** tab
- Check connection string
- View metrics

---

## Troubleshooting

### Build Fails

**Check:**
- Dockerfile path is correct
- `backend/` directory structure intact
- All required files exist (src/, alembic/, start.sh)

**Fix:**
```bash
# Test build locally
docker build -t test-build -f Dockerfile .
docker run -p 8000:8000 test-build
```

### Migrations Fail

**Check logs for Alembic errors:**
- Database connection (DATABASE_URL correct?)
- Missing tables or schema issues

**Fix:**
```bash
# Shell into Render service
# Dashboard → Service → Shell tab
alembic upgrade head  # Run manually
```

### Health Check Fails

**Common causes:**
1. **PORT mismatch** - start.sh uses `${PORT:-8000}`, Render sets PORT automatically
2. **App not ready** - Increase health check timeout to 60s
3. **Wrong path** - Verify `/health/live` endpoint works

**Fix:**
- Settings → Health Check → Increase timeout to 60s
- Or temporarily disable health check to see if app runs

### Workers Crash

**Check for:**
- Missing environment variables
- Database connection failures
- Import errors

**Fix:**
```bash
# Check logs for actual error
# Usually: "pydantic_settings.exceptions.SettingsError"
```

---

## Render vs Railway Differences

| Feature | Railway | Render |
|---------|---------|--------|
| **Free Tier** | $5 credit/month | 750 hours/month |
| **Cold Starts** | Minimal | ~30s on free tier |
| **Healthcheck** | Less reliable | More reliable |
| **Logs** | Real-time | Real-time |
| **Database** | Included | Included (free tier) |
| **Pricing** | Usage-based | Fixed ($7/month starter) |

---

## Next Steps

After backend deploys successfully:

1. **Update Frontend** - Add backend URL to Vercel environment:
   ```env
   NEXT_PUBLIC_API_URL=https://perpetua-backend.onrender.com
   ```

2. **Test OAuth** - Update Google OAuth redirect URLs:
   ```
   https://perpetua-backend.onrender.com/api/v1/auth/google/callback
   ```

3. **Custom Domain** (Optional):
   - Dashboard → Service → Settings → Custom Domain
   - Add: `api.yourdomain.com`
   - Configure DNS CNAME

---

## Cost Estimate

**Free Tier:**
- Web Service: Free (750 hours/month, spins down after 15min inactivity)
- PostgreSQL: Free (90 days, then $7/month)
- Total: **$0/month** (first 3 months)

**Paid Tier (Recommended for production):**
- Web Service: $7/month (always on, no cold starts)
- PostgreSQL: $7/month (persistent)
- Total: **$14/month**

---

## Support

- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com
