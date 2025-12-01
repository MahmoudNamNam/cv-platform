# 🚨 Fix 500 Error on Render - Quick Guide

Your app is deployed at: **https://cv-platform-xbq9.onrender.com/**

## Immediate Steps to Fix Registration Error

### Step 1: Check Health Endpoint

Visit: **https://cv-platform-xbq9.onrender.com/health/**

This will show you:
- Database connection status
- Whether migrations ran
- Environment variables

**Expected output:**
```json
{
  "status": "ok",
  "database": "connected",
  "migrations": "User table exists",
  "user_count": 0
}
```

**If you see "User table NOT found":**
→ Migrations haven't run! See Step 2.

---

### Step 2: Run Migrations (Most Common Fix)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click your service: **cv-platform**
3. Click **Shell** tab (or use the terminal icon)
4. Run these commands:

```bash
cd cv_platform
python manage.py migrate
```

**Wait for:** "Operations to perform: ... Applying ... OK"

5. Try registration again!

---

### Step 3: Check Render Logs

1. In Render Dashboard → Your Service
2. Click **Logs** tab
3. Look for **red error messages**
4. Common errors:

#### Error: "no such table: accounts_user"
**Fix:** Run migrations (Step 2)

#### Error: "UNIQUE constraint failed"
**Fix:** Username/email already exists - try different credentials

#### Error: "MongoDB connection failed"
**Fix:** Check `MONGODB_URI` environment variable

---

### Step 4: Verify Environment Variables

In Render Dashboard → Your Service → **Environment** tab:

**Required:**
- ✅ `DEBUG` = `False`
- ✅ `DJANGO_SECRET_KEY` = (long random string)
- ✅ `ALLOWED_HOSTS` = `cv-platform-xbq9.onrender.com`
- ✅ `MONGODB_URI` = `mongodb+srv://...`
- ✅ `MONGODB_DB_NAME` = `cv_platform`
- ✅ `COHERE_API_KEY` = (your key)

**Missing any?** Add them and redeploy!

---

### Step 5: Test Database Connection

In Render Shell:

```bash
cd cv_platform
python manage.py shell
```

Then in Python:
```python
from accounts.models import User
User.objects.all()  # Should return empty list, not error
```

**If error:** Database issue - check migrations

---

### Step 6: Create Test User Manually

In Render Shell:

```bash
cd cv_platform
python manage.py shell
```

```python
from accounts.models import User
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    role='student'
)
print(f"Created: {user.username}")
```

**If this works:** Registration should work too!
**If this fails:** Check the error message

---

## Quick Diagnostic Checklist

- [ ] Health endpoint shows "User table exists"
- [ ] Migrations have been run
- [ ] All environment variables are set
- [ ] Render logs show no errors
- [ ] Can create user via shell

---

## Still Not Working?

### Enable Debug Mode (Temporary)

1. In Render → Environment
2. Set `DEBUG=True`
3. Redeploy
4. Try registration - you'll see detailed error page
5. **Important:** Set back to `False` after!

### Check Procfile

File should be in project root:
```
release: cd cv_platform && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: PYTHONPATH=$PWD gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT
```

---

## Most Likely Issue

**90% of the time:** Migrations haven't run!

**Quick fix:**
```bash
# In Render Shell
cd cv_platform
python manage.py migrate --run-syncdb
```

Then try registration again!

---

## Need More Help?

See [RENDER_TROUBLESHOOTING.md](./RENDER_TROUBLESHOOTING.md) for detailed guide.

