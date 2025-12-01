# 🔧 MongoDB URI "Invalid URI scheme" Fix

## Error
```
Invalid URI scheme: URI must begin with 'mongodb://' or 'mongodb+srv://'
```

## Common Causes

### 1. **Quotes in Environment Variable** ⚠️ MOST COMMON

In Render Dashboard, if you set:
```
MONGODB_URI="mongodb+srv://user-12:aMC1i7aeYy2lcyvd@cluster0.mlhg3oy.mongodb.net/"
```

The quotes (`"`) are included in the value! This makes the URI invalid.

**Fix:** Remove the quotes when setting in Render:
```
MONGODB_URI=mongodb+srv://user-12:aMC1i7aeYy2lcyvd@cluster0.mlhg3oy.mongodb.net/
```

### 2. **Empty or Missing URI**

If `MONGODB_URI` is not set, it defaults to `mongodb://localhost:27017/`, but if it's set to an empty string, it will fail.

**Fix:** Ensure the URI is set correctly in Render Environment variables.

### 3. **Whitespace or Special Characters**

Extra spaces or hidden characters can break the URI.

**Fix:** The code now automatically strips whitespace and quotes, but double-check in Render.

## Step-by-Step Fix

### Step 1: Check Current Value in Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click your service → **Environment** tab
3. Find `MONGODB_URI`
4. **Check if it has quotes** around it

### Step 2: Update MONGODB_URI (Remove Quotes!)

1. Click **Edit** on `MONGODB_URI`
2. **Remove any quotes** (`"` or `'`) from the value
3. Set it to exactly:
   ```
   mongodb+srv://user-12:aMC1i7aeYy2lcyvd@cluster0.mlhg3oy.mongodb.net/
   ```
   **NO QUOTES!**

4. Click **Save Changes**

### Step 3: Verify MONGODB_DB_NAME

Ensure `MONGODB_DB_NAME` is set to:
```
cv_platform
```

### Step 4: Redeploy

1. Render will auto-redeploy after saving environment variables
2. Or manually trigger redeploy: **Manual Deploy** → **Deploy latest commit**

### Step 5: Check Logs

After redeploy, check Render logs for:
```
MongoDB client created successfully
```

If you see errors about URI scheme, the URI still has issues.

## What the Code Does Now

The updated code:
1. ✅ **Strips whitespace** from URI
2. ✅ **Removes quotes** (`"` and `'`) automatically
3. ✅ **Validates URI scheme** before using it
4. ✅ **Logs the actual URI value** for debugging

## Testing

After fixing, test the connection:

```bash
curl https://cv-platform-xbq9.onrender.com/health/
```

Should show MongoDB connection status.

## Still Not Working?

1. **Check Render logs** - Look for the actual URI value in error messages
2. **Verify in MongoDB Atlas** - Make sure the connection string is correct
3. **Try setting URI without trailing slash:**
   ```
   mongodb+srv://user-12:aMC1i7aeYy2lcyvd@cluster0.mlhg3oy.mongodb.net
   ```
   (The code will add `/cv_platform` automatically)

