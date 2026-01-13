# Enable GitHub Pages - Step by Step

## The Problem

You're getting a 404 error at https://agrabowski5.github.io/CANOPI_Prototyping because:
1. GitHub Pages is not enabled yet, OR
2. The deployment workflow hasn't completed successfully

---

## Solution: Enable GitHub Pages

### Step 1: Check Workflow Status

**Go to:** https://github.com/agrabowski5/CANOPI_Prototyping/actions

Look for the "Deploy" workflow run:
- 🟢 Green checkmark = Success
- 🔴 Red X = Failed
- 🟡 Yellow circle = In progress

**If still running:** Wait 2-5 minutes for it to complete.

**If failed:** Click on it to see error logs, then proceed to Step 2.

---

### Step 2: Enable GitHub Pages in Settings

1. **Go to repository settings:**

   👉 https://github.com/agrabowski5/CANOPI_Prototyping/settings/pages

2. **Under "Build and deployment":**

   - **Source:** Select "GitHub Actions" from dropdown

   ![image](https://docs.github.com/assets/cb-47267/mw-1440/images/help/pages/pages-source-settings.webp)

3. **Click "Save"**

4. **Wait 1-2 minutes** for GitHub to process

5. **Refresh the page** - you should see:
   ```
   Your site is live at https://agrabowski5.github.io/CANOPI_Prototyping/
   ```

---

### Step 3: Verify Deployment

Once enabled, trigger a new deployment:

**Option A: Push a small change**
```bash
cd C:\Users\agrab\OneDrive\Projects\CANOPI_Prototyping
git commit --allow-empty -m "Trigger deployment"
git push origin main
```

**Option B: Manually trigger workflow**
1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/actions/workflows/deploy.yml
2. Click "Run workflow"
3. Select "main" branch
4. Click "Run workflow"

---

### Step 4: Wait for Deployment

The workflow takes **3-5 minutes** to complete:

1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/actions
2. Watch for green checkmark ✓
3. Once complete, visit: https://agrabowski5.github.io/CANOPI_Prototyping

---

## Troubleshooting

### Still Getting 404?

#### Issue 1: Pages Not Enabled

**Check:**
- Go to: https://github.com/agrabowski5/CANOPI_Prototyping/settings/pages
- Is "Source" set to "GitHub Actions"?

**Fix:**
- Change "Source" to "GitHub Actions"
- Click "Save"
- Wait 2 minutes

---

#### Issue 2: Workflow Failed

**Check:**
- Go to: https://github.com/agrabowski5/CANOPI_Prototyping/actions
- Is there a red X?

**Common Errors:**

**Error: "Resource not accessible by integration"**
```
Fix: Enable workflow permissions
1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/settings/actions
2. Under "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Click "Save"
6. Re-run the workflow
```

**Error: "MAPBOX_ACCESS_TOKEN not set"**
```
Fix: Add Mapbox secret
1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/settings/secrets/actions
2. Click "New repository secret"
3. Name: MAPBOX_ACCESS_TOKEN
4. Value: [your Mapbox token]
5. Click "Add secret"
6. Re-run the workflow
```

**Error: "npm ci failed"**
```
Fix: Build might need --legacy-peer-deps flag
- Already configured in deploy.yml
- Check workflow logs for specific error
```

---

#### Issue 3: Wrong Branch

**Check:**
- GitHub Pages might be looking at wrong branch

**Fix:**
1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/settings/pages
2. Make sure "Source" is "GitHub Actions" (not a branch like gh-pages)
3. If it says "Deploy from a branch", change to "GitHub Actions"

---

#### Issue 4: Cache Issue

**Check:**
- Your browser might be caching the 404

**Fix:**
1. Hard refresh: **Ctrl + Shift + R** (Windows) or **Cmd + Shift + R** (Mac)
2. Clear browser cache
3. Try incognito/private window
4. Try different browser

---

### Check Deployment Status Programmatically

```bash
# Check if site is up (should return 200)
curl -I https://agrabowski5.github.io/CANOPI_Prototyping/

# Check if Pages is enabled (requires gh CLI)
gh api repos/agrabowski5/CANOPI_Prototyping/pages
```

---

## Expected Result

After following these steps, you should see:

**At the URL:** https://agrabowski5.github.io/CANOPI_Prototyping

**The CANOPI application with:**
- ✅ Map loads
- ✅ No 404 errors in console
- ✅ "New Project" button works
- ✅ Projects panel visible
- ✅ Optimization panel visible

---

## Alternative: Check if Build Artifacts Exist

1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/actions
2. Click latest "Deploy" workflow run
3. Click "deploy-frontend" job
4. Check "Upload artifact" step
5. Should show: "Artifact download URL: ..."

If artifact exists but site is 404, it's definitely a Pages settings issue.

---

## Quick Checklist

- [ ] Workflow completed successfully (green checkmark)
- [ ] GitHub Pages enabled in settings
- [ ] Source set to "GitHub Actions"
- [ ] Workflow permissions set to "Read and write"
- [ ] Waited 2-5 minutes after enabling
- [ ] Hard refreshed browser (Ctrl + Shift + R)
- [ ] Tried incognito/private window

---

## Current Status Check

**To verify your current setup:**

1. **Workflows:** https://github.com/agrabowski5/CANOPI_Prototyping/actions
   - Latest run status?

2. **Pages Settings:** https://github.com/agrabowski5/CANOPI_Prototyping/settings/pages
   - Is source "GitHub Actions"?

3. **Actions Permissions:** https://github.com/agrabowski5/CANOPI_Prototyping/settings/actions
   - Are permissions "Read and write"?

---

## Contact for Help

If still having issues after following all steps:

1. **Check workflow logs:**
   - Go to failed workflow
   - Click on each job
   - Look for red error messages
   - Share the error message

2. **Check Pages settings:**
   - Screenshot the Pages settings page
   - Share what "Source" is set to

3. **Check URL:**
   - Is it exactly: https://agrabowski5.github.io/CANOPI_Prototyping/
   - Try with and without trailing slash

---

**Last Updated:** January 13, 2026
