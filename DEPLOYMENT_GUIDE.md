# 🚀 Deployment Guide - LaTeX Resume Agent

## 📋 Table of Contents
1. [Hosting Platform Recommendations](#hosting-platforms)
2. [GitHub OAuth Configuration](#github-oauth)
3. [Environment Variables Setup](#environment-variables)
4. [Docker Deployment](#docker-deployment)
5. [Production Checklist](#production-checklist)

---

## 🌐 Hosting Platform Recommendations

### **Recommended: Railway.app** ⭐
**Best for:** Docker Compose projects with multiple services

**Pros:**
- ✅ Supports Docker Compose natively
- ✅ Free tier: 500 hours/month (~20 days)
- ✅ $5 credit on signup
- ✅ PostgreSQL/Redis add-ons available
- ✅ Automatic HTTPS
- ✅ GitHub integration for auto-deploy
- ✅ Environment variable management

**Free Tier Limits:**
- 500 execution hours/month
- 512MB RAM per service
- Sleeps after 1 hour inactivity (starter plan)

**Setup Steps:**
1. Sign up at https://railway.app
2. Connect GitHub repository
3. Deploy from Dockerfile
4. Add environment variables
5. Get your production URL (e.g., `https://your-app.railway.app`)

---

### Alternative: Render.com
**Best for:** Separate service deployment

**Pros:**
- ✅ Free tier for web services
- ✅ Auto-deploy from GitHub
- ✅ Built-in PostgreSQL
- ✅ Automatic HTTPS
- ✅ Health checks

**Cons:**
- ⚠️ Free tier spins down after inactivity (50 sec startup)
- ⚠️ Limited to 750 hours/month

---

### Alternative: Fly.io
**Best for:** Docker-first deployment

**Pros:**
- ✅ Full Docker support
- ✅ 3 GB persistent volume
- ✅ 160GB bandwidth
- ✅ Global edge network

**Cons:**
- ⚠️ Requires credit card
- ⚠️ Complex pricing structure

---

## 🔑 GitHub OAuth Configuration

### Step 1: Update GitHub OAuth App Settings

1. Go to: https://github.com/settings/developers
2. Click on **OAuth Apps**
3. Find your app: **LaTeX Resume Agent**
4. Update these fields:

```
Application name: LaTeX Resume Agent
Homepage URL: https://your-domain.com
Authorization callback URL: https://your-domain.com/api/auth/callback/github
```

### Step 2: Replace Placeholder Domains

**For Railway.app:**
```
Homepage URL: https://your-app.railway.app
Callback URL: https://your-app.railway.app/api/auth/callback/github
```

**For Render.com:**
```
Homepage URL: https://your-app.onrender.com
Callback URL: https://your-app.onrender.com/api/auth/callback/github
```

### Step 3: Update Environment Variables

After getting your production URL, update these in your hosting platform:

**Backend (.env):**
```bash
GITHUB_CALLBACK_URL=https://your-domain.com/api/auth/callback/github
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_APP_URL=https://your-domain.com
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## 🔐 Environment Variables Setup

### Backend Environment Variables (`backend/.env`)

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./latex_agent.db

# Redis
REDIS_URL=redis://redis:6379/0

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Gemini API Keys (3-key rotation)
GEMINI_API_KEY_1=AIzaSyCoVZyLDuFNON0XFesAiTPsuV8yrEn3bU8
GEMINI_API_KEY_2=AIzaSyB3cidtJW37_6vXcnCIq_YNsKbzYXVGot4
GEMINI_API_KEY_3=AIzaSyCet85qQPbPp_BpMAikbuhqbcTUqXOiSl4

# GitHub OAuth
GITHUB_CLIENT_ID=0v23117PyDDHv0U1oqbZ
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_CALLBACK_URL=https://your-domain.com/api/auth/callback/github

# JWT Secret (generate a new one for production!)
JWT_SECRET=your-super-secret-key-change-this-in-production

# App Settings
ENVIRONMENT=production
```

### Frontend Environment Variables (`frontend/.env.local`)

```bash
# API URL (backend)
NEXT_PUBLIC_API_URL=https://your-api-domain.com

# GitHub OAuth
NEXT_PUBLIC_GITHUB_CLIENT_ID=0v23117PyDDHv0U1oqbZ

# App URL (for OAuth callbacks)
NEXT_PUBLIC_APP_URL=https://your-domain.com
```

### Generate Secure JWT Secret

Run this in your terminal:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# OpenSSL
openssl rand -base64 32
```

---

## 🐳 Docker Deployment

### Option 1: Deploy with Docker Compose (Recommended for Railway)

```bash
# Build and run all services
docker-compose up --build -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down
```

### Option 2: Deploy Individual Services (Recommended for Render)

**Backend:**
```bash
cd backend
docker build -t latex-agent-backend .
docker run -p 8000:8000 --env-file .env latex-agent-backend
```

**Frontend:**
```bash
cd frontend
docker build -t latex-agent-frontend .
docker run -p 3000:3000 --env-file .env.local latex-agent-frontend
```

### Docker Compose Configuration Notes

✅ **Already configured:**
- PostgreSQL removed (using SQLite for simplicity)
- Production-ready CMD (no --reload flag)
- Volume mounts for database persistence
- Environment variable support
- Health checks for Redis

---

## ✅ Production Checklist

### Before Deployment

- [ ] Generate new JWT secret (don't use default!)
- [ ] Update GitHub OAuth callback URL
- [ ] Set all environment variables in hosting platform
- [ ] Remove any hardcoded localhost URLs
- [ ] Test Docker build locally: `docker-compose up --build`
- [ ] Verify `.env` is in `.gitignore`
- [ ] Create production `.env` files (don't commit them!)

### After Deployment

- [ ] Test GitHub OAuth login flow
- [ ] Test resume generation
- [ ] Check API endpoints: `/health`, `/api/auth/profile`
- [ ] Verify database persistence
- [ ] Monitor logs for errors
- [ ] Test file uploads
- [ ] Verify LaTeX compilation works

### Security Checklist

- [ ] Use HTTPS (automatic on Railway/Render/Fly)
- [ ] Rotate API keys if needed
- [ ] Enable CORS only for your frontend domain
- [ ] Set secure cookie flags in production
- [ ] Review and limit file upload sizes
- [ ] Enable rate limiting for API endpoints

---

## 🔧 Common Issues & Solutions

### Issue: "Database is locked" (SQLite)

**Solution:** SQLite doesn't handle concurrent writes well. For production, consider PostgreSQL:

```bash
# In docker-compose.yml, uncomment PostgreSQL service
# Update backend/.env:
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/latex_agent
```

### Issue: OAuth redirect mismatch

**Solution:** Ensure these match exactly:
- GitHub OAuth callback URL
- `GITHUB_CALLBACK_URL` in backend/.env
- `NEXT_PUBLIC_APP_URL` in frontend/.env.local

### Issue: Frontend can't reach backend API

**Solution:** Check CORS configuration in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "Module not found" errors

**Solution:** Rebuild Docker images:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Monitoring & Logs

### View Logs

**Docker Compose:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Railway:**
- View logs in Railway dashboard
- Enable log streaming for real-time monitoring

**Render:**
- Logs available in service dashboard
- Download logs for debugging

---

## 💰 Cost Estimation

### Railway.app (Recommended)
- **Free Tier:** 500 hours/month + $5 credit
- **Hobby Plan:** $5/month per service
- **Estimated Cost:** $0-10/month for small usage

### Render.com
- **Free Tier:** Web service + PostgreSQL
- **Starter Plan:** $7/month per service
- **Estimated Cost:** $0-14/month

### Fly.io
- **Free Tier:** 3 small VMs
- **Pay-as-you-go:** ~$5-15/month
- **Estimated Cost:** $0-15/month

---

## 🎯 Quick Start Commands

```bash
# 1. Update environment variables
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# Edit both files with production values

# 2. Build and test locally
docker-compose up --build

# 3. Push to GitHub
git add .
git commit -m "Configure for production deployment"
git push origin main

# 4. Deploy on Railway
# - Connect repository
# - Configure environment variables
# - Deploy!

# 5. Update GitHub OAuth callback URL
# - Go to https://github.com/settings/developers
# - Update callback URL with your Railway domain
```

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Test locally with Docker before deploying
4. Review this guide's troubleshooting section

---

**Ready to deploy? Start with Railway.app for the easiest experience!** 🚀
