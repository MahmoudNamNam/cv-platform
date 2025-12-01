# Free Deployment Guide - CV Platform

This guide will help you deploy the CV Platform application for **FREE** using popular hosting platforms.

## 🆓 Free Hosting Options

1. **Render** (Recommended) - Free tier with 750 hours/month
2. **Railway** - Free $5 credit monthly
3. **Fly.io** - Free tier with generous limits

---

## 📋 Prerequisites

Before deploying, you'll need:

1. ✅ **GitHub account** (free)
2. ✅ **MongoDB Atlas account** (free tier - 512MB)
3. ✅ **Cohere API key** (free tier available)
4. ✅ Your code pushed to GitHub

---

## 🗄️ Step 1: Set Up MongoDB Atlas (FREE)

MongoDB Atlas offers a free tier with 512MB storage:

### 1.1 Create MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Sign up for a free account
3. Create a new **FREE** cluster (M0 tier)

### 1.2 Configure Database Access

1. Go to **Database Access** → **Add New Database User**
2. Choose **Password** authentication
3. Create username and password (save these!)
4. Set privileges to **Atlas Admin** (or read/write to specific database)

### 1.3 Configure Network Access

1. Go to **Network Access** → **Add IP Address**
2. Click **Allow Access from Anywhere** (0.0.0.0/0)
   - Or add your hosting platform's IP ranges

### 1.4 Get Connection String

1. Go to **Database** → Click **Connect** on your cluster
2. Choose **Connect your application**
3. Copy the connection string
   - It will look like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
4. Replace `<password>` with your database user password
5. Add database name: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/cv_platform?retryWrites=true&w=majority`

**Save this connection string!** You'll need it for deployment.

---

## 🚀 Step 2: Deploy to Render (FREE - RECOMMENDED)

Render offers 750 free hours/month (enough for 1 web service running 24/7).

### 2.1 Prepare Your Repository

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/cv-platform.git
   git push -u origin main
   ```

### 2.2 Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Sign up/login with GitHub
3. Click **New +** → **Web Service**
4. Connect your GitHub repository
5. Configure the service:

   **Basic Settings:**
   - **Name**: `cv-platform` (or any name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)

   **Build & Deploy:**
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && cd cv_platform && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```bash
     cd cv_platform && gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT
     ```

### 2.3 Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `DEBUG` | `False` | Production mode |
| `DJANGO_SECRET_KEY` | Generate a random key | Use: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Replace with your Render URL |
| `MONGODB_URI` | Your MongoDB Atlas connection string | From Step 1.4 |
| `MONGODB_DB_NAME` | `cv_platform` | |
| `COHERE_API_KEY` | Your Cohere API key | Get from [Cohere](https://dashboard.cohere.com/) |

### 2.4 Deploy!

1. Click **Create Web Service**
2. Render will build and deploy automatically
3. Wait 5-10 minutes for first deployment
4. Your app will be live at: `https://your-app-name.onrender.com`

### 2.5 Create Admin User (One-Time)

1. Go to **Shell** in Render dashboard
2. Run:
   ```bash
   cd cv_platform
   python manage.py createsuperuser
   ```
3. Follow prompts to create admin account

---

## 🚂 Step 3: Alternative - Deploy to Railway (FREE)

Railway offers $5 free credit monthly (enough for small apps).

### 3.1 Deploy on Railway

1. Go to [Railway](https://railway.app/)
2. Sign up/login with GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your repository

### 3.2 Configure Environment Variables

Go to **Variables** tab and add the same variables as Render (Step 2.3)

### 3.3 Set Start Command

1. Go to **Settings** → **Deploy**
2. Set **Start Command**:
   ```bash
   cd cv_platform && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT
   ```

### 3.4 Generate Domain

1. Go to **Settings** → **Generate Domain**
2. Railway will assign a free domain (e.g., `your-app.railway.app`)
3. Update `ALLOWED_HOSTS` environment variable with this domain

---

## 🪂 Step 4: Alternative - Deploy to Fly.io (FREE)

Fly.io offers a generous free tier with 3 shared-cpu VMs.

### 4.1 Install Fly CLI

```bash
# Mac/Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### 4.2 Create Fly App

1. Login:
   ```bash
   fly auth login
   ```

2. Initialize app:
   ```bash
   fly launch
   ```

3. Follow prompts:
   - App name: (auto-generated or choose one)
   - Region: Choose closest
   - PostgreSQL: **No** (we use MongoDB)
   - Redis: **No**

### 4.3 Create fly.toml

Create `fly.toml` in project root:

```toml
app = "your-app-name"
primary_region = "iad"

[build]

[env]
  DEBUG = "False"
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### 4.4 Set Secrets

```bash
fly secrets set DJANGO_SECRET_KEY="your-secret-key"
fly secrets set MONGODB_URI="your-mongodb-uri"
fly secrets set MONGODB_DB_NAME="cv_platform"
fly secrets set COHERE_API_KEY="your-cohere-key"
fly secrets set ALLOWED_HOSTS="your-app-name.fly.dev"
```

### 4.5 Create Dockerfile

Fly.io uses Docker. Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
WORKDIR /app/cv_platform
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start server
CMD python manage.py migrate --noinput && gunicorn cv_platform.wsgi:application --bind 0.0.0.0:8000
```

### 4.6 Deploy

```bash
fly deploy
```

---

## 🔧 Step 5: Post-Deployment Setup

### 5.1 Create Admin User

Run migrations and create superuser:

```bash
# Render: Use Shell in dashboard
# Railway: Use CLI or dashboard terminal
# Fly.io: Use fly ssh console

cd cv_platform
python manage.py migrate
python manage.py createsuperuser
```

### 5.2 Verify Deployment

1. Visit your deployed URL
2. Test registration and login
3. Test CV upload (if media storage configured)
4. Check admin panel: `https://your-app-url.com/admin/`

---

## 📝 Important Notes

### Static Files
- ✅ Static files are served via WhiteNoise (already configured)
- ✅ No additional CDN needed for small apps

### Media Files (CV Uploads)
- ⚠️ **Important**: Free hosting platforms may not persist uploaded files
- **Solutions**:
  1. Use **Cloudinary** (free tier) for media storage
  2. Use **AWS S3** (free tier: 5GB storage)
  3. Use **MongoDB GridFS** (stored in your Atlas database)

### SQLite Database
- The app uses SQLite for Django auth (stored in filesystem)
- On free platforms, this may reset on redeploy
- **Solution**: Consider using **PostgreSQL** (free on Render/Railway) if needed

### Environment Variables
Always keep these secure:
- `DJANGO_SECRET_KEY` - Never commit to git
- `COHERE_API_KEY` - Keep private
- `MONGODB_URI` - Contains password

---

## 🆘 Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError`
- **Fix**: Check `requirements.txt` has all dependencies

**Error**: `collectstatic failed`
- **Fix**: Ensure `STATIC_ROOT` is set correctly in settings.py

### App Won't Start

**Error**: `PORT not set`
- **Fix**: Ensure hosting platform sets `$PORT` environment variable

**Error**: `MongoDB connection failed`
- **Fix**: 
  1. Check MongoDB Atlas network access (allow all IPs)
  2. Verify connection string format
  3. Check username/password

### Static Files Not Loading

- **Fix**: Ensure WhiteNoise middleware is in `MIDDLEWARE` (already added)
- **Fix**: Run `collectstatic` during build

---

## 📊 Cost Breakdown (FREE)

| Service | Free Tier |
|---------|-----------|
| **Render** | 750 hours/month (1 web service 24/7) |
| **Railway** | $5 credit/month |
| **Fly.io** | 3 shared-cpu VMs |
| **MongoDB Atlas** | 512MB storage |
| **Cohere API** | Free tier available |

**Total Cost: $0/month** ✅

---

## 🔗 Quick Links

- [Render Dashboard](https://dashboard.render.com/)
- [Railway Dashboard](https://railway.app/)
- [Fly.io Dashboard](https://fly.io/dashboard)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Cohere Dashboard](https://dashboard.cohere.com/)

---

## 🎉 Success!

Once deployed, your CV Platform will be live and accessible from anywhere!

**Next Steps:**
- Share your app URL with users
- Monitor usage in hosting dashboard
- Set up backups for MongoDB Atlas
- Consider adding custom domain (optional, may have costs)

---

**Need Help?** Check the platform-specific documentation or open an issue in your repository.

