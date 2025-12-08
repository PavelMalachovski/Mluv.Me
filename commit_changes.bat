@echo off
cd C:\Git\Mluv.Me
git add .
git status
git diff --cached --name-only
echo.
echo Ready to commit? Press Enter to continue...
pause
git commit -m "fix: web ui hostname, reverse proxy and cache first greeting only"
git push
echo.
echo Done!
pause
