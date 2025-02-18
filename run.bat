@echo off
cd /d %~dp0

echo Activating virtual environment...
pipenv shell

start cmd /k "pipenv run uvicorn api:app --reload"
timeout /t 5 >nul
start cmd /k "pipenv run streamlit run dashboard.py"

pause
exit
