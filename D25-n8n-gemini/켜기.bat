@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=..\D25-mcp\p2-team\.venv\Scripts\python.exe
if not exist "%PY%" (
  echo [!] p2-team 가상환경이 없어요. p2-team 폴더에서: python -m venv .venv ^&^& .venv\Scripts\pip install mcp
  pause & exit /b 1
)
echo [1/3] 우리 조 MCP (team) 를 HTTP 로 켜요 - 새 창이 열려요 (닫으면 꺼져요)
start "team MCP :8765" "%PY%" -X utf8 team_http.py

echo [2/3] n8n 켜기 (Docker Desktop 이 켜져 있어야 해요)
docker start n8n-d25 >nul 2>&1
if errorlevel 1 (
  docker run -d --name n8n-d25 -p 127.0.0.1:5678:5678 -v n8n_d25_data:/home/node/.n8n -v "%~dp0.:/files:ro" -e GENERIC_TIMEZONE=Asia/Seoul -e TZ=Asia/Seoul -e N8N_DIAGNOSTICS_ENABLED=false -e N8N_PERSONALIZATION_ENABLED=false n8nio/n8n:latest
  timeout /t 8 >nul
  docker exec n8n-d25 n8n import:workflow --input=/files/워크플로_우리조_챗봇.json
)

echo [3/3] 브라우저로 n8n 열기
timeout /t 5 >nul
start http://localhost:5678
