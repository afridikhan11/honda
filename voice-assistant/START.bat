@echo off
cd /d %~dp0
if not exist venv (echo Pehle SETUP.bat chalayein & pause & exit /b 1)
call venv\Scripts\activate
python agent.py
pause
