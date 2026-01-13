# Installation & Troubleshooting Guide

Complete guide for installing, configuring, and troubleshooting the CANOPI frontend.

## System Requirements

### Minimum Requirements
- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher (comes with Node.js)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for dependencies

### Supported Operating Systems
- ✅ Windows 10/11
- ✅ macOS 12+ (Monterey or later)
- ✅ Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)

### Supported Browsers
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Pre-Installation Checklist

- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm 9+ installed (`npm --version`)
- [ ] Git installed (for cloning)
- [ ] Mapbox account created
- [ ] Backend API accessible
- [ ] Internet connection (for npm packages)

## Installation Steps

### Step 1: Install Node.js

#### Windows
```bash
# Download from https://nodejs.org/
# Run the installer
# Verify installation
node --version
npm --version
```

#### macOS
```bash
# Using Homebrew
brew install node

# Verify
node --version
npm --version
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version
npm --version
```

### Step 2: Navigate to Frontend Directory

```bash
cd CANOPI_Prototyping/frontend
```

### Step 3: Install Dependencies

```bash
npm install
```

This will install:
- React 18.2.0
- TypeScript 5.3.3
- Redux Toolkit 2.0.1
- Mapbox GL JS 3.1.0
- Tailwind CSS 3.4.0
- Axios 1.6.5
- React Router 6.21.1
- And ~30 other dependencies

**Expected time**: 2-5 minutes depending on internet speed

### Step 4: Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env with your favorite editor
nano .env
# or
code .env
# or
notepad .env
```

Add your Mapbox token:
```env
REACT_APP_MAPBOX_TOKEN=pk.your_actual_token_here
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENABLE_MOCK_DATA=true
REACT_APP_ENABLE_DARK_MODE=true
```

### Step 5: Get Mapbox Token

1. Go to https://account.mapbox.com/
2. Sign up (free tier is sufficient)
3. Navigate to "Access Tokens"
4. Copy your default public token (starts with `pk.`)
5. Paste into `.env` file

**Token Scopes Required**:
- ✅ styles:read
- ✅ tiles:read
- ✅ fonts:read

### Step 6: Start Development Server

```bash
npm start
```

The app should open automatically at http://localhost:3000

If it doesn't open automatically, manually navigate to http://localhost:3000

## Verification

### 1. Check Dev Server

You should see:
```
Compiled successfully!

You can now view canopi-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

### 2. Check Browser Console

Open DevTools (F12) and check console:
- ✅ No red errors
- ⚠️ Yellow warnings are usually okay

### 3. Check Map Loading

- ✅ Map should render
- ✅ You should be able to zoom/pan
- ✅ Layer controls visible in top-left

### 4. Check Backend Connection

Open browser Network tab and verify:
- ✅ Requests to `localhost:8000` succeed (or show CORS error if backend not running)

## Common Issues & Solutions

### Issue 1: "npm: command not found"

**Problem**: Node.js/npm not installed or not in PATH

**Solution**:
```bash
# Windows: Reinstall Node.js from nodejs.org
# macOS: brew install node
# Linux: Follow Step 1 above

# Verify installation
node --version
npm --version
```

### Issue 2: "Port 3000 already in use"

**Problem**: Another app is using port 3000

**Solution 1**: Kill the process
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Or use this shortcut
npx kill-port 3000
```

**Solution 2**: Use different port
```bash
PORT=3001 npm start
```

### Issue 3: "Module not found" errors

**Problem**: Dependencies not installed correctly

**Solution**:
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Issue 4: Mapbox map not loading

**Symptoms**:
- Blank map area
- Console error: "Error: A valid Mapbox access token is required"

**Solution**:
1. Verify token in `.env` file
2. Ensure token starts with `pk.`
3. Check token hasn't expired
4. Restart dev server after adding token
5. Clear browser cache

**Debug Steps**:
```bash
# Check if .env exists
ls -la .env

# Check token is set
cat .env | grep MAPBOX

# Restart server
npm start
```

### Issue 5: "Cannot connect to backend"

**Symptoms**:
- Projects don't load
- Optimization fails
- Console shows network errors

**Solution**:
1. Verify backend is running
```bash
# In backend directory
uvicorn app.main:app --reload
```

2. Check backend URL in `.env`
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

3. Check CORS settings in backend

4. Verify backend health
```bash
curl http://localhost:8000/health
```

### Issue 6: TypeScript errors

**Problem**: Type errors during development

**Solution**:
```bash
# Clear TypeScript cache
rm -rf node_modules/.cache

# Restart dev server
npm start

# Or rebuild
npm run build
```

### Issue 7: Slow compilation / High CPU usage

**Problem**: Development server using too much resources

**Solution**:
1. Close other applications
2. Increase Node.js memory
```bash
NODE_OPTIONS=--max_old_space_size=4096 npm start
```

3. Disable source maps temporarily
```bash
GENERATE_SOURCEMAP=false npm start
```

### Issue 8: Hot reload not working

**Problem**: Changes not reflecting in browser

**Solution**:
1. Create `.env.local`
```bash
echo "FAST_REFRESH=true" > .env.local
```

2. Clear browser cache
```bash
# Or hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (macOS)
```

3. Restart dev server

### Issue 9: Dark mode not working

**Problem**: Dark mode toggle doesn't change styles

**Solution**:
1. Verify Tailwind is configured
```bash
# Check tailwind.config.js exists
ls tailwind.config.js
```

2. Check `darkMode` setting
```javascript
// tailwind.config.js
darkMode: 'class',  // Should be 'class' not 'media'
```

3. Clear PostCSS cache
```bash
rm -rf node_modules/.cache
npm start
```

### Issue 10: Build fails

**Problem**: `npm run build` fails with errors

**Solution**:
1. Check for TypeScript errors
```bash
npx tsc --noEmit
```

2. Fix any errors shown

3. Clear and rebuild
```bash
rm -rf build node_modules
npm install
npm run build
```

## Performance Issues

### Issue: Slow map rendering

**Solutions**:
1. Reduce number of visible markers
2. Use clustering for many projects
3. Disable unnecessary layers
4. Lower map quality on slow devices

### Issue: Slow page load

**Solutions**:
1. Enable production build optimizations
2. Lazy load components
3. Optimize images
4. Enable caching

## Development Tips

### Hot Reload Optimization

```bash
# Add to .env.local
FAST_REFRESH=true
REACT_APP_REFRESH=true
```

### TypeScript Performance

```bash
# Skip TypeScript checks during dev (faster)
TSC_COMPILE_ON_ERROR=true npm start
```

### Source Maps

```bash
# Disable source maps for faster builds
GENERATE_SOURCEMAP=false npm start
```

## Production Build

### Build for Production

```bash
npm run build
```

**Expected Output**:
```
Creating an optimized production build...
Compiled successfully.

File sizes after gzip:

  200 KB    build/static/js/main.abc123.js
  50 KB     build/static/css/main.xyz456.css

The build folder is ready to be deployed.
```

### Test Production Build Locally

```bash
# Install serve
npm install -g serve

# Serve build directory
serve -s build

# Open http://localhost:3000
```

### Deploy Production Build

See deployment guides for:
- Vercel: `vercel deploy`
- Netlify: Drag `build/` folder to Netlify
- AWS S3: `aws s3 sync build/ s3://your-bucket`

## Environment-Specific Issues

### Windows-Specific

1. **PowerShell Execution Policy**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. **Path separators**
Use forward slashes or double backslashes in paths

3. **Line endings**
Configure git to use LF:
```bash
git config --global core.autocrlf input
```

### macOS-Specific

1. **Permission denied**
```bash
sudo chown -R $USER /usr/local/lib/node_modules
```

2. **Command Line Tools**
```bash
xcode-select --install
```

### Linux-Specific

1. **Permission errors**
```bash
sudo npm install -g npm
sudo chown -R $USER ~/.npm
```

2. **Missing dependencies**
```bash
sudo apt-get install build-essential
```

## Monitoring & Debugging

### Browser DevTools

1. **Console**: Check for errors
2. **Network**: Monitor API calls
3. **Elements**: Inspect styling
4. **React DevTools**: Inspect components
5. **Redux DevTools**: Debug state

### Logs

```bash
# Enable verbose logging
DEBUG=* npm start

# Save logs to file
npm start > output.log 2>&1
```

### Performance Profiling

```bash
# Build with profiling
npm run build -- --profile

# Or use React Profiler in DevTools
```

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Search GitHub issues
3. Read error messages carefully
4. Check browser console
5. Verify backend is running

### When Asking for Help

Include:
- Node.js version (`node --version`)
- npm version (`npm --version`)
- Operating system
- Error messages (full text)
- Steps to reproduce
- Screenshots if relevant

### Resources

- GitHub Issues: Report bugs
- Stack Overflow: General questions
- Mapbox Support: Mapping issues
- React Docs: React questions

## Maintenance

### Update Dependencies

```bash
# Check for updates
npm outdated

# Update all (careful!)
npm update

# Update specific package
npm update react
```

### Security Updates

```bash
# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix

# Fix with breaking changes
npm audit fix --force
```

### Clean Install

```bash
# Remove everything
rm -rf node_modules package-lock.json build .cache

# Fresh install
npm install
```

## Success Checklist

After installation, verify:
- [ ] Dev server starts without errors
- [ ] Map loads and displays correctly
- [ ] Can create projects by clicking map
- [ ] Projects appear in left sidebar
- [ ] Can run optimization
- [ ] Dark mode toggle works
- [ ] No console errors
- [ ] Backend connection works

## Next Steps

Once everything is working:
1. Read [QUICK_START.md](./QUICK_START.md) for first steps
2. Explore [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
3. Check [README.md](./README.md) for feature documentation
4. Start building!

## Support

If you're still having issues after following this guide:
1. Check the GitHub repository for known issues
2. Create a new issue with details
3. Ask in the project Discord/Slack (if available)

Good luck! 🚀
