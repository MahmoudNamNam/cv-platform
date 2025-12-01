# 🔧 Fix 500 Error on Render (Free Plan - No Shell Access)

Since you can't access Shell on Render's free plan, here are alternative ways to fix the registration error.

## ✅ Solution 1: Use Web Endpoint to Run Migrations (Easiest)

### Step 1: Set Setup Token

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click your service → **Environment** tab
3. Add new environment variable:
   - **Key**: `SETUP_TOKEN`
   - **Value**: Create a random secret (e.g., `my-secret-token-12345`)
4. Click **Save Changes**
5. Wait for automatic redeploy (or manually redeploy)

### Step 2: Run Migrations via Web

**Option A: Using curl (from your computer)**

```bash
curl -X POST https://cv-platform-xbq9.onrender.com/setup/run-migrations/ \
  -H "Content-Type: application/json" \
  -d '{"token": "my-secret-token-12345"}'
```

**Option B: Using Browser (JavaScript Console)**

1. Open your site: https://cv-platform-xbq9.onrender.com/
2. Press `F12` to open Developer Tools
3. Go to **Console** tab
4. Paste and run:

```javascript
fetch('https://cv-platform-xbq9.onrender.com/setup/run-migrations/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({token: 'my-secret-token-12345'})
})
.then(r => r.json())
.then(data => console.log(data))
.catch(e => console.error(e));
```

Replace `my-secret-token-12345` with your actual token!

**Expected Response:**
```json
{
  "success": true,
  "message": "Migrations completed",
  "user_table_exists": true
}
```

### Step 3: Test Registration

After migrations run successfully, try registering again!

---

## ✅ Solution 2: Trigger Redeploy (Automatic Migrations)

Your `Procfile` has a `release` command that runs migrations automatically. To trigger it:

### Method 1: Manual Redeploy

1. Go to Render Dashboard → Your Service
2. Click **Manual Deploy** → **Deploy latest commit**
3. Wait for deployment to complete
4. The `release` command will run migrations automatically

### Method 2: Push Empty Commit

```bash
# On your local computer
git commit --allow-empty -m "Trigger redeploy to run migrations"
git push
```

This triggers a new deployment, which runs the `release` command.

---

## ✅ Solution 3: Check Health Endpoint First

Before running migrations, check the current status:

Visit: **https://cv-platform-xbq9.onrender.com/health/**

**If you see:**
```json
{
  "migrations": "User table NOT found - migrations needed!"
}
```

→ Migrations need to run! Use Solution 1 or 2.

**If you see:**
```json
{
  "migrations": "User table exists"
}
```

→ Migrations already ran. The issue might be something else.

---

## ✅ Solution 4: Update Build Command (Render Settings)

1. Go to Render Dashboard → Your Service
2. Click **Settings** tab
3. Scroll to **Build Command**
4. Set it to:
   ```bash
   pip install -r requirements.txt && cd cv_platform && python manage.py migrate --run-syncdb --noinput && python manage.py collectstatic --noinput
   ```
5. Click **Save Changes**
6. Redeploy

---

## 🔍 Verify It Worked

### Check Health Endpoint

Visit: https://cv-platform-xbq9.onrender.com/health/

Should show:
```json
{
  "status": "ok",
  "database": "connected",
  "migrations": "User table exists",
  "user_count": 0
}
```

### Try Registration

1. Go to: https://cv-platform-xbq9.onrender.com/accounts/register/
2. Fill the form
3. Submit

**If it works:** ✅ Success!

**If still 500 error:** Check Render logs (Dashboard → Logs tab) for the actual error message.

---

## 🚨 Troubleshooting

### Migration Endpoint Returns 403

**Problem:** `SETUP_TOKEN` not set or wrong token

**Fix:**
1. Check `SETUP_TOKEN` in Render Environment variables
2. Use the exact same token in your request
3. Make sure you saved and redeployed after adding the token

### Migration Endpoint Returns 500

**Problem:** Migration failed

**Fix:**
1. Check the error message in the response
2. Common issues:
   - Database locked (wait a few seconds and try again)
   - Missing dependencies (check requirements.txt)

### Still Getting 500 After Migrations

**Possible causes:**
1. **MongoDB connection issue** - Check `MONGODB_URI` environment variable
2. **Missing environment variables** - Verify all required vars are set
3. **Form validation error** - Check browser console (F12) for client-side errors

**Check Render Logs:**
1. Render Dashboard → Your Service → **Logs** tab
2. Look for red error messages
3. The logs will show the actual error

---

## 📋 Quick Checklist

- [ ] Set `SETUP_TOKEN` environment variable in Render
- [ ] Check health endpoint: `/health/`
- [ ] Run migrations via `/setup/run-migrations/` endpoint
- [ ] Verify health endpoint shows "User table exists"
- [ ] Try registration again
- [ ] Check Render logs if still failing

---

## 🎯 Recommended Approach

**For immediate fix:**
1. Use Solution 1 (Web Endpoint) - fastest
2. Set `SETUP_TOKEN` in Render
3. Run migrations via curl or browser console
4. Test registration

**For long-term:**
- Solution 2 (Redeploy) ensures migrations always run
- The `release` command in Procfile handles this automatically

---

## 💡 Pro Tip

After fixing, you can remove or change the `SETUP_TOKEN` for security. The migrations only need to run once (unless you add new models).

---

**Need more help?** Check the error message in Render logs and share it for specific troubleshooting!

