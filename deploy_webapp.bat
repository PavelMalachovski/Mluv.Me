@echo off
echo ===========================================
echo   Deploying Telegram Web App Integration
echo ===========================================
echo.

cd C:\Git\Mluv.Me

echo [1/5] Checking git status...
git status
echo.

echo [2/5] Adding files...
git add .
echo.

echo [3/5] Files to commit:
git diff --cached --name-only
echo.

echo [4/5] Committing changes...
git commit -m "feat: add telegram web app integration with auto-auth"
echo.

echo [5/5] Pushing to GitHub...
git push
echo.

echo ===========================================
echo   Deployment Complete!
echo ===========================================
echo.
echo Railway will auto-deploy in 2-3 minutes.
echo.
echo NEXT STEPS:
echo.
echo 1. Wait for Railway deployment to finish
echo 2. Open @BotFather in Telegram
echo 3. Send: /mybots
echo 4. Select your bot
echo 5. Bot Settings -^> Menu Button
echo 6. Button Text: 🎓 Открыть приложение
echo 7. URL: https://mluvme-production.up.railway.app
echo.
echo 8. Open your bot in Telegram
echo 9. Click Menu button (☰)
echo 10. Enjoy! 🎉
echo.
pause
