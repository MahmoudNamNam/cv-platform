# 🚀 Quick Free Deployment Guide

Deploy your CV Platform **100% FREE** in under 10 minutes!

## 📋 What You Need (All Free)

- ✅ GitHub account
- ✅ MongoDB Atlas account (free 512MB)
- ✅ Cohere API key (free tier)
- ✅ Render account (750 free hours/month)

---

## ⚡ 3-Step Deployment

### Step 1: MongoDB Atlas Setup (5 min)

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas/register)
2. Sign up → Create FREE cluster (M0)
3. **Database Access**: Create user with password
4. **Network Access**: Allow from anywhere (0.0.0.0/0)
5. **Connect** → Copy connection string:
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/cv_platform?retryWrites=true&w=majority
   ```

### Step 2: Push to GitHub (2 min)

```bash
git init
git add .
git commit -m "Ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cv-platform.git
git push -u origin main
```

### Step 3: Deploy on Render (3 min)

1. Go to [render.com](https://dashboard.render.com/)
2. **New +** → **Web Service**
3. Connect GitHub repo
4. Configure:
   - **Name**: `cv-platform`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && cd cv_platform && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```bash
     gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT
     ```
     ⚠️ **Important**: Do NOT use `cd cv_platform &&` before gunicorn. Run gunicorn from the project root.
5. Add Environment Variables:
   ```
   DEBUG=False
   DJANGO_SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=your-app-name.onrender.com
   MONGODB_URI=your-mongodb-connection-string
   MONGODB_DB_NAME=cv_platform
   COHERE_API_KEY=your-cohere-key
   ```
6. Click **Create Web Service**
7. Wait 5-10 minutes... ✅ **Done!**

---

## 🎯 Your App is Live!

Visit: `https://your-app-name.onrender.com`

### First-Time Setup

1. Go to **Shell** in Render dashboard
2. Run:
   ```bash
   cd cv_platform
   python manage.py createsuperuser
   ```
3. Create admin account

---

## 🔑 Get Your Keys

### Cohere API Key
- Go to [dashboard.cohere.com](https://dashboard.cohere.com/)
- Sign up → Get free API key

### Django Secret Key
Run this locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## ✅ That's It!

Your CV Platform is now live and free! 🎉

**Total Cost: $0/month**  
**Setup Time: ~10 minutes**

Need more details? See [DEPLOYMENT.md](./DEPLOYMENT.md) for full guide.

