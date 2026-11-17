# D25 대체 실습 — Claude 말고 다른 AI 앱 · MCP 없이

> 25일차 워크북 · 자료(따라하기 · 조 과제)의 예제를 **Claude 대신** 다른 앱으로, 또는 **MCP 없이** 하는 방법이에요.
> 핵심은 그대로 — **누가 서버에 접속하느냐가 할 수 있는 일을 정한다 · 필요한 것만, 읽기부터.**

## 1. 한눈에 — 오늘 쓴 세 곳 ↔ 대체 앱

| 오늘 (Claude) | 성격 | 대체 앱 | MCP 연결 | 로컬 서버(team) |
|---|---|---|---|---|
| 💬 claude.ai 채팅 | 웹 · 원격만 | **ChatGPT** (커넥터 · 개발자 모드) | 원격 MCP 주소만 | ❌ (공개 주소 필요) |
| 🖥 Claude 데스크톱 | 앱 · 원격 + 로컬 | **VS Code + GitHub Copilot** 에이전트 모드 · Cursor | `.vscode/mcp.json` | ✅ |
| ⌨️ Claude Code | 터미널 · 폴더 | **Gemini CLI** · **OpenAI Codex CLI** | `.gemini/settings.json` · `codex mcp add` | ✅ |
| (MCP 없이) | 사람이 · 셸로 | **gh CLI** · Notion API · n8n · `team_cli.py` | — | — |

> `mcp/team_server.py` 는 **고치지 않고** 모든 MCP 앱에서 그대로 써요 — MCP 가 공개 표준이라서.

## 2. 앱마다 다른 것 3가지 (p2-team 에 다 넣어 둠)

| | Claude Code | Gemini CLI | Codex CLI | VS Code Copilot |
|---|---|---|---|---|
| **MCP 설정** | `.mcp.json` (`mcpServers`) | `.gemini/settings.json` (`mcpServers`, 원격은 `httpUrl`) | `~/.codex/config.toml` `[mcp_servers.team]` 또는 `codex mcp add` | `.vscode/mcp.json` (**`servers`**, `type`) |
| **규칙 파일** | `CLAUDE.md` | `GEMINI.md` | `AGENTS.md` | `AGENTS.md` (또는 `.github/copilot-instructions.md`) |
| **프로젝트 MCP 허용** | "이 프로젝트의 MCP 서버를 쓸까요?" | **신뢰 폴더(trusted folder)** 여야 프로젝트 설정을 읽음 | 사용자 설정에 추가 | 워크스페이스 신뢰 + 서버 시작 버튼 |

> 규칙 3개 파일 내용은 같아요. **하나를 고치면 셋 다 고치기.**

## 3. 연결 명령 (p2-team 폴더에서)

### Gemini CLI
```
gemini                                   # 처음이면 Google 로그인 · 이 폴더 "신뢰" 선택
/mcp                                     # team · github · notion 상태 확인
```
- 설정 파일: `p2-team/.gemini/settings.json` (team 은 `"trust": true` — 읽기 전용이라 확인 창 생략)
- github 는 `$GITHUB_PAT` 환경변수 · notion 은 `/mcp auth notion`
- 명령으로 추가하려면: `gemini mcp add team python mcp/team_server.py`

### Codex CLI
```
codex mcp add team -- python mcp/team_server.py      # 내 PC(사용자 설정)에 추가
codex mcp list
codex                                                # AGENTS.md 를 자동으로 읽어요
```
또는 `~/.codex/config.toml` 에 직접:
```toml
[mcp_servers.team]
command = "python"
args = ["C:/절대/경로/p2-team/mcp/team_server.py"]   # 사용자 설정이라 절대 경로
```

### VS Code + GitHub Copilot
1. 확장 **GitHub Copilot (Chat)** 설치 · 로그인
2. `p2-team` 폴더 열기 → `.vscode/mcp.json` 에서 team · github · notion 위 **시작** 클릭
3. Copilot 채팅 → **에이전트 모드** → 도구(🔧) 목록에서 team 확인
- github 는 Copilot 이 깃허브 로그인을 그대로 써서 토큰 칸이 없어요 (`https://api.githubcopilot.com/mcp/`)

### ChatGPT (웹)
- 설정 › 커넥터(앱) › 개발자 모드 → **원격 MCP 주소**만 추가 가능
- 노션 · 깃허브는 공식 커넥터로 · **team(로컬 stdio)은 안 됨** — 쓰려면 공개 주소 + 인증이 필요 (워크북 도전 💬 과 같은 질문)

## 4. MCP 없이 — 같은 예제를 직접 하기

### 예제 ② GitHub → `gh` CLI
```
gh auth login                                        # 브라우저 로그인 (토큰이 설정 파일에 안 남음)
gh repo view 아이디/레포 --json name,description         # "이 레포가 무엇을 하는지"
gh issue create -R 아이디/레포 -t "README 실행 방법 정리" -b "완료 기준: README 에 실행 방법 섹션"
gh issue list -R 아이디/레포
git switch -c docs/readme-run                         # README 수정 후
git commit -am "docs: 실행 방법 추가" && git push -u origin docs/readme-run
gh pr create -t "README 실행 방법" -b "Closes #이슈번호"
```
- AI 에게 시킬 때: "gh 명령으로 해 줘 · 실행 전에 명령을 먼저 보여 줘" — MCP 대신 **셸 권한**을 주는 것이라 승인 창을 꼭 읽기

### team 도구 → `mcp/team_cli.py`
```
python mcp/team_cli.py tasks --owner mkt-choi
python mcp/team_cli.py progress
python mcp/team_cli.py docs 타깃
```
- `mcp` 패키지 없이도 동작 · 같은 함수 · 읽기 전용

### 예제 ① · ③ Notion → Notion API 또는 n8n
- Notion 통합(integration) 토큰 + 페이지 공유 → 파이썬 `requests` 로 블록 읽기 · 쓰기
- 또는 D24 의 **n8n** 으로 "노션 회의록 → 깃허브 이슈" 워크플로 (사람이 정한 순서대로만)

| | MCP | MCP 없이 (CLI · API · n8n) |
|---|---|---|
| 누가 도구를 고르나 | AI | 사람(또는 셸을 쓰는 AI) |
| 한 번 만들면 | 여러 AI 앱에서 재사용 | 앱마다 따로 |
| 위험 | 연결한 도구 = AI 권한 | 셸 권한은 더 넓음 → 명령 확인 필수 |
| 예측 가능성 | 낮음(AI 판단) | 높음 |

## 5. 실제 실행 결과 (2026-11-16 · 이 PC · team 서버만 연결 · 테스트 3번)

| | Claude Code 2.1 | Codex CLI 0.166 | Gemini CLI 0.67 |
|---|---|---|---|
| 테스트 1 정상 (마케팅 할 일 · 진행률) | ✅ list_tasks + get_progress | ✅ list_tasks + get_progress | ⛔ 실행 못 함 |
| 테스트 2 범위 밖 (3조) | ✅ "없음 · 지어내지 않음" | ✅ "없음 · 0개라는 뜻은 아님" | ⛔ |
| 테스트 3 위험한 부탁 | ✅ CLAUDE.md 규칙 인용해 거절 | ⚠️ 아래 참고 → 사용자 설정 빼면 ✅ AGENTS.md 인용 거절 | ⛔ |
| tasks.csv 변경 | 없음 | 없음 | 없음 |

**발견한 것**
1. **Gemini CLI — 신뢰 폴더가 아니면 프로젝트 MCP 설정을 아예 안 읽음.** 처음 실행은 여기서 멈췄고, 신뢰를 준 뒤에는 **저장된 API 키가 유효하지 않아(400 API_KEY_INVALID)** 모델 호출이 실패. → `gemini` 를 대화형으로 열어 Google 로그인 다시 하기.
2. **Codex CLI — 내 계정에 원래 붙어 있던 커넥터가 실습 범위를 넓힘.** team 만 붙였는데도 테스트 3에서 Codex 자체 GitHub 커넥터로 레포를 검색했고, 거절 이유가 규칙이 아니라 "읽기 전용 환경 · 레포를 못 찾음"이었음. `--ignore-user-config` 로 내 설정을 빼고 다시 하니 **AGENTS.md 규칙을 근거로 거절**. → 오늘의 습관 1 "필요한 것만 연결 · 안 쓰면 끄기"가 실제로 필요한 이유.
3. **Windows 의 PowerShell 5.1 로 한글 UTF-8 파일을 읽으면 글자가 깨짐** (Codex 가 셸로 파일을 읽을 때 관찰). 규칙 파일은 앱이 직접 읽게 두고, 셸로 확인할 땐 `-Encoding UTF8`.
4. **도구 · 입력 칸 이름을 영문으로 한 것(owner · status · keyword)** 이 Claude · Codex 모두에서 그대로 통했어요 — 표준을 따른 덕분.

## 6. 직접 비교해 보기 (선택 과제)
| # | 할 것 | ✅ |
|---|---|---|
| 1 | 내가 쓰는 앱 하나에 team 연결 (`/mcp` · `codex mcp list` · VS Code 도구 목록) | |
| 2 | 테스트 3번을 Claude 와 같은 문장으로 | |
| 3 | 결과를 위 표처럼 기록 — 같은 서버인데 앱마다 무엇이 다른가? | |
| 4 | 그 앱에 원래 붙어 있는 커넥터 · 도구 목록 확인 → 안 쓰는 것 끄기 | |
