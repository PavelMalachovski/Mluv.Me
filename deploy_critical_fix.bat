@echo off
echo ====================================
echo   CRITICAL FIX - API URL для Web App
echo ====================================
echo.
echo Проблема: localhost:8000 не работает в Telegram Web App
echo Решение: Используем window.location.origin
echo.
cd C:\Git\Mluv.Me
echo [1/4] Git status...
git status --short
echo.
echo [2/4] Добавляем файлы...
git add .
echo.
echo [3/4] Коммитим...
git commit -m "fix: use relative API URLs for Telegram Web App compatibility"
echo.
echo [4/4] Пушим на Railway...
git push
echo.
echo ====================================
echo   Готово!
echo ====================================
echo.
echo Railway задеплоит через 2-3 минуты
echo.
echo После деплоя:
echo 1. Откройте бота в Telegram
echo 2. Menu -^> Continue with Telegram
echo 3. Проверьте консоль (F12)
echo 4. Должен быть редирект на /dashboard!
echo.
pause
