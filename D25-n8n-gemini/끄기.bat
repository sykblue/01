@echo off
chcp 65001 >nul
echo n8n 을 꺼요 (워크플로 · 자격 증명은 n8n_d25_data 볼륨에 남아요)
docker stop n8n-d25
echo team MCP 창("team MCP :8765")은 직접 닫아 주세요.
pause
