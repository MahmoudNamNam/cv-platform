# 🔧 Render Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. 500 Error on Registration

**Symptoms:**
- Registration form returns 500 Internal Server Error
- No error message shown to user

**Possible Causes & Solutions:**

#### A. Database Migrations Not Run
**Check:** Go to Render Dashboard → Your Service → Logs
Look for migration errors.

**Fix:**
1. Go to Render Dashboard → Your Service → **Shell**
2. Run:
   ```bash
   cd cv_platform
   python manage.py migrate
   ```
3. Redeploy your service

#### B. SQLite Database Issues
**Problem:** Render's filesystem is ephemeral - SQLite database may reset.

**Check Logs:**
```bash
# In Render Shell
cd cv_platform
python manage.py dbshell
```

**Solution:** This is expected on Render. The SQLite database resets on each deploy. Consider:
- Using PostgreSQL (free on Render) for production
- Or accept that user auth data resets on redeploy

#### C. Missing Environment Variables
**Check:** Render Dashboard → Environment tab

**Required Variables:**
```
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=cv-platform-xbq9.onrender.com
MONGODB_URI=your-mongodb-connection-string
MONGODB_DB_NAME=cv_platform
COHERE_API_KEY=your-cohere-key
```

**Fix:**
1. Go to Render Dashboard → Your Service → **Environment**
2. Add missing variables
3. Redeploy

#### D. Database Connection Error
**Check Logs for:**
```
OperationalError: no such table: accounts_user
```

**Fix:**
```bash
# In Render Shell
cd cv_platform
python manage.py migrate --run-syncdb
```

---

### 2. Check Application Logs

**Steps:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click your service
3. Click **Logs** tab
4. Look for error messages (red text)

**Common Log Errors:**

#### "No module named 'cv_platform'"
**Fix:** Ensure Procfile uses correct path:
```
web: PYTHONPATH=$PWD gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT
```

#### "Table doesn't exist"
**Fix:** Run migrations in Shell:
```bash
cd cv_platform
python manage.py migrate
```

#### "MongoDB connection failed"
**Fix:** 
1. Check `MONGODB_URI` environment variable
2. Verify MongoDB Atlas network access (allow all IPs)
3. Check connection string format

---

### 3. Test Registration Manually

**Using Render Shell:**
1. Go to Render Dashboard → Your Service → **Shell**
2. Run:
   ```bash
   cd cv_platform
   python manage.py shell
   ```
3. In Python shell:
   ```python
   from accounts.models import User
   from django.contrib.auth import get_user_model
   
   # Check if User model works
   User.objects.all()
   
   # Try creating a user
   user = User.objects.create_user(
       username='testuser',
       email='test@example.com',
       password='testpass123',
       role='student'
   )
   print(f"User created: {user.username}")
   ```

If this fails, check the error message.

---

### 4. Quick Fixes

#### Fix 1: Re-run Migrations
```bash
# In Render Shell
cd cv_platform
python manage.py migrate --run-syncdb
python manage.py migrate
```

#### Fix 2: Create Admin User
```bash
# In Render Shell
cd cv_platform
python manage.py createsuperuser
```

#### Fix 3: Check Database
```bash
# In Render Shell
cd cv_platform
python manage.py dbshell
# Then in SQLite:
.tables
.schema accounts_user
```

#### Fix 4: Collect Static Files
```bash
# In Render Shell
cd cv_platform
python manage.py collectstatic --noinput
```

---

### 5. Verify Environment Variables

**Check in Render Dashboard:**
1. Go to your service
2. Click **Environment** tab
3. Verify all required variables are set:

| Variable | Example Value |
|----------|---------------|
| `DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | `django-insecure-...` (long random string) |
| `ALLOWED_HOSTS` | `cv-platform-xbq9.onrender.com` |
| `MONGODB_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DB_NAME` | `cv_platform` |
| `COHERE_API_KEY` | `your-api-key-here` |

---

### 6. Enable Debug Mode (Temporary)

**For debugging only:**
1. In Render Dashboard → Environment
2. Set `DEBUG=True`
3. Redeploy
4. Try registration again - you'll see detailed error
5. **Important:** Set back to `False` after debugging!

---

### 7. Check Procfile

**Current Procfile should be:**
```
release: cd cv_platform && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: PYTHONPATH=$PWD gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT
```

**Verify:**
- File is in project root (not in cv_platform/)
- No extra spaces
- Line endings are correct

---

### 8. Common Registration Errors

#### Error: "UNIQUE constraint failed"
**Cause:** Username or email already exists
**Fix:** Use different username/email

#### Error: "no such table: accounts_user"
**Cause:** Migrations not run
**Fix:** Run migrations (see Fix 1 above)

#### Error: "role field required"
**Cause:** Form validation issue
**Fix:** Check form is sending role field

---

### 9. Test Your Deployment

**Health Check:**
Visit: `https://cv-platform-xbq9.onrender.com/`

**Test Registration:**
1. Go to `/accounts/register/`
2. Fill form
3. Check browser console (F12) for errors
4. Check Render logs for server errors

---

### 10. Get Help

**If still having issues:**

1. **Check Render Logs:**
   - Dashboard → Your Service → Logs
   - Look for stack traces

2. **Enable Debug Mode:**
   - Set `DEBUG=True` temporarily
   - See detailed error page

3. **Check Database:**
   ```bash
   # In Render Shell
   cd cv_platform
   python manage.py showmigrations
   ```

4. **Verify All Files:**
   - Procfile exists in root
   - requirements.txt has all dependencies
   - settings.py is configured correctly

---

## Quick Diagnostic Commands

Run these in Render Shell to diagnose:

```bash
cd cv_platform

# Check Python version
python --version

# Check Django
python manage.py version

# Check migrations
python manage.py showmigrations

# Check environment
python -c "import os; print(os.getenv('DEBUG')); print(os.getenv('MONGODB_URI'))"

# Test database
python manage.py dbshell
```

---

## Still Stuck?

1. Copy error from Render logs
2. Check browser console errors (F12)
3. Verify all environment variables
4. Try creating user via shell (see section 3)

The most common issue is **migrations not running**. Always check that first!

