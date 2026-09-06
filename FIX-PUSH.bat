@echo off
cd /d D:\Project\HondaWorkshopWeb
git remote remove origin 2>nul
git remote add origin https://github.com/afridikhan11/honda.git
git add -A
git commit -m "Honda Islamabad update"
git push -u origin main
echo.
echo ===== AGAR UPAR KOI ERROR NAHI TO PUSH HO GAYA =====
pause
