@echo off
cd C:\Git\Mluv.Me
echo Checking status...
git status
echo.
echo Adding files...
git add .
echo.
echo Files to commit:
git diff --cached --name-only
echo.
echo Committing...
git commit -m "fix: move catch-all proxy route to end - critical fix for web ui"
echo.
echo Pushing to GitHub...
git push
echo.
echo Done! Railway will auto-deploy in 2-3 minutes.
echo.
echo To check your app URL:
echo 1. Go to Railway Dashboard
echo 2. Click on your service
echo 3. Go to Settings -^> Domains
echo 4. Copy the URL (something like: mluv-me-production.up.railway.app)
echo 5. Open that URL in browser
echo.
pause
