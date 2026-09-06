@echo off
cd /d D:\Project\HondaWorkshopWeb
if not exist .git (
  git init
  git branch -M main
  git remote add origin https://github.com/afridikhan11/honda.git
)
git add -A
git commit -m "Honda Islamabad update"
git pull --no-edit origin main
git push -u origin main
echo.
echo ===== PUSH HO GAYA! Cloudflare khud deploy karega (1-2 minute) =====
pause
