@echo off
echo ================================
echo   Quick Fix - Web App Freeze
echo ================================
echo.
cd C:\Git\Mluv.Me
git add .
git commit -m "fix: disable auto-auth, add manual button and logging"
git push
echo.
echo ================================
echo   Deployed!
echo ================================
echo.
echo Wait 2-3 minutes for Railway to deploy.
echo.
echo Then:
echo 1. Open bot in Telegram
echo 2. Click Menu button
echo 3. Click "Continue with Telegram" button
echo 4. Check browser console (F12) for logs
echo.
pause
