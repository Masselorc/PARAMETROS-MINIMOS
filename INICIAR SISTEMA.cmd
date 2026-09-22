@echo off
cd /d "%~dp0"
title Parametros Minimos - ONASP (http://127.0.0.1:8000)

if not exist "DADOS.xlsx" (
  echo [ERRO] DADOS.xlsx nao encontrado nesta pasta.
  echo Coloque o DADOS.xlsx na raiz do projeto e tente novamente.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Criando ambiente virtual...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERRO] Falha ao criar .venv. Verifique se o Python 3.12+ esta instalado.
    pause
    exit /b 1
  )
)

echo Verificando dependencias...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo [ERRO] Falha ao instalar dependencias.
  pause
  exit /b 1
)

echo.
echo Antes de editar pelo sistema, feche o DADOS.xlsx no Excel.
echo Iniciando em http://127.0.0.1:8000 ...
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000

pause
