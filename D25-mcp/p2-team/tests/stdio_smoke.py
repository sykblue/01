"""stdio 연결 시험 — Claude Code 처럼 team_server.py 를 실행해서 도구 목록을 받고 3개를 불러 봐요.

실행:  python tests/stdio_smoke.py        (p2-team 폴더에서, pip install mcp 필요)
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def main():
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(ROOT, "mcp", "team_server.py")])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print("도구:", [f"{t.name}({t.title})" for t in tools])
            ro = lambda a: bool(a and (getattr(a, "read_only_hint", None) or getattr(a, "readOnlyHint", None)))
            print("읽기 전용 표시:", [ro(t.annotations) for t in tools])
            for name, args in (("list_tasks", {"owner": "po-park"}), ("get_progress", {}), ("search_docs", {"keyword": "타깃"})):
                res = await s.call_tool(name, args)
                text = " ".join(getattr(c, "text", "") for c in res.content)
                print(f"\n▶ {name}({json.dumps(args, ensure_ascii=False)})\n{text[:400]}")


if __name__ == "__main__":
    asyncio.run(main())
