@echo off
cd /d %~dp0
echo ===== AI Assistant setup (sirf pehli dafa) =====
python --version >nul 2>&1 || (
  echo Python nahi mila. https://www.python.org/downloads/ se Python 3.12 ya 3.13 install karein
  echo Install karte waqt "Add python.exe to PATH" par tick zaroor lagayein.
  pause & exit /b 1
)
if not exist venv python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt || (echo !! Install mein masla aaya, upar error dekhein & pause & exit /b 1)
if not exist .env copy .env.example .env >nul
echo.
echo ===== Setup mukammal! =====
echo Ab .env file Notepad mein khul rahi hai - apni free Gemini key daal kar save karein.
notepad .env
pause
