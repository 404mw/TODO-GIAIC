# Deployment & Configuration Guide - Perpetua Flow

## ✅ Code Verification Summary

I've verified all the code you need for Google OAuth and Checkout.com integration:

### Frontend (002-perpetua-frontend branch) ✅
- **OAuth Service:** `frontend/src/lib/services/oauth.service.ts` - Fully implemented
- **Payment Service:** `frontend/src/lib/services/payment.service.ts` - Fully implemented
- **Login Page:** `/login` with Google OAuth button
- **OAuth Callback:** `/auth/callback` handler
- **Protected Routes:** Dashboard layout with auth checks

### Backend (003-perpetua-backend branch) ✅
- **Google OAuth:** `/api/v1/auth/google/callback` - Token verification implemented
- **Checkout Webhook:** `/api/v1/webhooks/checkout` - **Signature verification already implemented!**
- **Subscription API:** All subscription endpoints ready
- **Payment Processing:** Credit purchase and subscription flows ready

---

## 🎯 What You Need to Configure

### 1. Google OAuth Environment Variables

#### Vercel (Frontend)
```bash
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
```

#### Backend Server
```bash
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here
```

### 2. Checkout.com Environment Variables

#### Vercel (Frontend)
```bash
NEXT_PUBLIC_CHECKOUT_PUBLIC_KEY=pk_sbox_xxxxx
```

#### Backend Server
```bash
CHECKOUT_SECRET_KEY=sk_sbox_xxxxx
CHECKOUT_WEBHOOK_SECRET=whsec_xxxxx  # ← Your Signature Key!
```

---

## ✅ OAuth Implementation Status

**COMPLETED!** The frontend has been updated to use Google's Sign-In SDK.

### What Was Implemented

1. ✅ Installed `@react-oauth/google` package
2. ✅ Updated `login/page.tsx` to use GoogleOAuthProvider and GoogleLogin
3. ✅ Updated `oauth.service.ts` with `authenticateWithGoogle()` method
4. ✅ Configured to send Google ID token to backend `/auth/google/callback`
5. ✅ Added environment variable validation for NEXT_PUBLIC_GOOGLE_CLIENT_ID

### How It Works Now

```tsx
// login/page.tsx now uses Google Sign-In SDK
<GoogleOAuthProvider clientId={NEXT_PUBLIC_GOOGLE_CLIENT_ID}>
  <GoogleLogin
    onSuccess={handleGoogleSuccess}
    onError={handleGoogleError}
    useOneTap
  />
</GoogleOAuthProvider>

// oauth.service.ts sends ID token to backend
await oauthService.authenticateWithGoogle(credentialResponse.credential)
// → POST /api/v1/auth/google/callback with { id_token: "..." }
```

The implementation is complete and ready for deployment once environment variables are configured.

---

## ✅ Backend Webhook Verification

**Already implemented perfectly!** (backend/src/api/subscription.py:222)

```python
# Verify webhook signature (FR-048)
checkout_client = get_checkout_client(settings)
if not checkout_client.verify_signature(body, signature):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid webhook signature",
    )
```

This matches exactly what I recommended. Just add the `CHECKOUT_WEBHOOK_SECRET` environment variable!

---

## 📋 Complete Environment Variables List

### Vercel (Frontend Production)

```bash
# Build Settings
Root Directory: frontend

# API
NEXT_PUBLIC_API_URL=https://your-backend.com

# OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=123-abc.apps.googleusercontent.com

# Payments
NEXT_PUBLIC_CHECKOUT_PUBLIC_KEY=pk_sbox_xxxxx

# Features
NEXT_PUBLIC_AI_ENABLED=false
NEXT_PUBLIC_MSW_ENABLED=false
NEXT_PUBLIC_MAX_TASKS=50
NEXT_PUBLIC_MAX_SUBTASKS_PER_TASK=10
```

### Backend Production

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# JWT
JWT_PRIVATE_KEY_PATH=/path/to/keys/private.pem
JWT_PUBLIC_KEY_PATH=/path/to/keys/public.pem
JWT_ALGORITHM=RS256

# Google OAuth
GOOGLE_CLIENT_ID=123-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx

# Checkout.com
CHECKOUT_SECRET_KEY=sk_sbox_xxxxx
CHECKOUT_WEBHOOK_SECRET=whsec_xxxxx  # Signature Key

# AI
OPENAI_API_KEY=sk-xxxxx
DEEPGRAM_API_KEY=xxxxx

# CORS
FRONTEND_URL=https://perpetua-flow.vercel.app
```

---

## 🧪 Testing Steps

### 1. Test Google OAuth
```
1. Go to https://perpetua-flow.vercel.app/login
2. Click "Sign in with Google"
3. Complete Google consent
4. Should redirect to /dashboard with token
```

### 2. Test Checkout.com Webhook
```
1. In Checkout.com dashboard → Webhooks
2. Click "Send test event"
3. Choose "payment_approved"
4. Check backend logs for signature verification success
```

### 3. Test Payment Flow
```
1. Go to /dashboard/credits
2. Click "Purchase Credits"
3. Use test card: 4242 4242 4242 4242
4. CVV: 100 (success) or 200 (decline)
5. Verify credits added after webhook
```

---

## 🚀 Deployment Checklist

- [ ] Google OAuth credentials created
- [ ] Authorized redirect URIs configured (for One Tap: https://perpetua-flow.vercel.app)
- [ ] Checkout.com webhook configured
- [ ] All environment variables added to Vercel
- [ ] All environment variables added to backend server
- [x] Frontend OAuth SDK installed (`@react-oauth/google`) ✅
- [x] Frontend login page updated to use Google Sign-In SDK ✅
- [x] OAuth service updated to send ID token to backend ✅
- [ ] Backend deployed and accessible
- [ ] CORS configured to allow frontend domain
- [ ] Database migrations run
- [ ] Test OAuth flow end-to-end
- [ ] Test payment flow with sandbox card
- [ ] Verify webhook signature verification works

---

## 🐛 Troubleshooting

### OAuth "Invalid redirect URI"
✅ **Fix:** Ensure `https://perpetua-flow.vercel.app/auth/callback` is in Google Console

### Webhook "Invalid signature"
✅ **Fix:** Double-check `CHECKOUT_WEBHOOK_SECRET` matches the **Signature Key** (not Authorization Header)

### CORS Errors
✅ **Fix:** Add `FRONTEND_URL=https://perpetua-flow.vercel.app` to backend env

---

## 📝 Summary

**Code Status:** ✅ All code already implemented correctly!

**What you need:**
1. Add environment variables to Vercel
2. Add environment variables to backend
3. Install `@react-oauth/google` in frontend
4. Update login page to use Google SDK
5. Test the flows

Everything else is already done! 🎉
