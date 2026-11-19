@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto erro
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto erro
echo Instalacao concluida. Edite config.py e execute executar.bat.
pause
exit /b 0
:erro
echo Falha na instalacao. Confira as mensagens acima.
pause
exit /b 1
