# p2-team — 우리 조 MCP 레포 (D25 조 과제 템플릿)

```
p2-team/
├ .mcp.json             github · notion · team 공유 세트 (토큰은 ${GITHUB_PAT} 이름만)
├ CLAUDE.md             우리 조 AI 규칙 (Claude Code)
├ GEMINI.md · AGENTS.md  같은 규칙 — Gemini CLI · Codex · Copilot 용
├ .gemini/settings.json · .vscode/mcp.json   다른 AI 앱용 MCP 설정 (../대체/README.md)
├ tasks.csv             할 일 (칸 이름 그대로: 번호,할 일,직군,담당자,상태,마감)
├ docs/                 회의록 · 기획서
├ mcp/team_server.py    ★ 우리 조 MCP (읽기 전용 · 도구 3개)
├ mcp/team_cli.py       같은 도구를 MCP 없이 명령줄로
└ tests/                검증 체크 자동 테스트
```

## 받기 · 연결 (조원 모두)
```
git clone https://github.com/camp2-○조-주제/p2-team.git
cd p2-team
pip install mcp
claude
```
- "이 프로젝트의 MCP 서버를 쓸까요?" → 허용 → `/mcp` › notion › Authenticate
- 토큰: Windows `setx GITHUB_PAT "토큰"` 후 VS Code 완전히 재시작 · Mac `~/.zshrc` 에 export

## 우리 조 MCP (team)
| 도구 이름 (제목) | 하는 일 |
|---|---|
| `list_tasks` (할일_보기 · owner=담당자, status=상태) | tasks.csv 거르기 (빈 값이면 전체) |
| `get_progress` (진행률) | 직군별 완료/전체 · 전체 진행률 |
| `search_docs` (문서_찾기 · keyword=키워드) | docs/*.md 에서 키워드가 있는 줄 (최대 30개) |

- 도구 이름은 MCP 표준(SEP-986)상 영문 · 숫자 · `_` 만 가능 → 한글은 제목(title) · 설명에.
- 입력 칸 이름도 영문(owner · status · keyword) — 한글이면 Claude 가 도구를 못 써요. 한국어 설명은 그대로 붙어 있어요.
- 세 도구 모두 `readOnlyHint` (읽기 전용 표시) 가 붙어 있어요.
- mcp 2.x 는 `from mcp.server import MCPServer`, 1.x 는 `from mcp.server.fastmcp import FastMCP` — 서버 코드가 둘 다 지원해요.

일부러 만들지 않은 도구: 할 일 추가 · 수정 · 삭제, 이슈 닫기, 파일 저장 — 사람이 PR 로.

## 시험
```
python -m unittest discover -s tests -v     # 검증 체크 5개 + 동작 3개
python tests/stdio_smoke.py                 # Claude Code 처럼 실행해서 도구 3개 호출
npx @modelcontextprotocol/inspector python mcp/team_server.py
```

## 실행 방법
1. `pip install mcp`
2. `python mcp/team_server.py` (stdio — 직접 실행하면 입력을 기다리며 멈춰 있는 게 정상, Ctrl+C 로 종료)
3. Claude Code 에서는 `.mcp.json` 으로 자동 실행
