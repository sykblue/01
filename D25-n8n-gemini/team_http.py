"""우리 조 MCP(team_server.py)를 HTTP 로 여는 실행 파일 — n8n 이 접속할 수 있게.

n8n 의 MCP Client Tool 은 '주소(URL)'로만 접속해요 (stdio ❌).
그래서 같은 서버를 그대로 가져와 http://127.0.0.1:8765/mcp 로 열어요. 도구 · 규칙은 그대로 (읽기 전용 3개).

실행 (p2-team 가상환경 python):
  ..\\D25-mcp\\p2-team\\.venv\\Scripts\\python.exe team_http.py
n8n(도커) 에서 쓰는 주소:  http://host.docker.internal:8765/mcp
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "D25-mcp", "p2-team", "mcp"))
import team_server as ts  # noqa: E402

from mcp.server.transport_security import TransportSecuritySettings  # noqa: E402

PORT = int(os.environ.get("TEAM_HTTP_PORT", "8765"))

if __name__ == "__main__":
    if ts.mcp is None:
        sys.exit("mcp 패키지가 없어요 — p2-team 의 .venv python 으로 실행하세요")
    # 내 PC(127.0.0.1)에서만 열고, 도커 안 n8n 이 부르는 이름(host.docker.internal)만 추가로 허용
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["127.0.0.1:*", "localhost:*", "host.docker.internal:*"],
        allowed_origins=[],
    )
    print(f"team MCP (읽기 전용) → http://127.0.0.1:{PORT}/mcp   · n8n 에서는 http://host.docker.internal:{PORT}/mcp")
    ts.mcp.run(transport="streamable-http", host="127.0.0.1", port=PORT, transport_security=security)
