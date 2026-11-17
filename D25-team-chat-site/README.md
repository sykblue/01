# P2 조 도우미 — 우리 조 챗봇 사이트 (배포 가능)

> D25 n8n 챗봇(Ollama Qwen + team MCP)을 **혼자 서는 웹사이트**로 옮긴 버전.
> 왼쪽은 진행 현황 대시보드, 오른쪽은 챗봇 — 챗봇이 어떤 도구를 불렀는지 🔧 칩으로 보여 줘요.

```
브라우저 ── /api/team  → 대시보드 (할 일 · 직군별 진행률)
        └─ /api/chat  → lib/agent.js ─ LLM (OpenAI 호환: Ollama · Groq · Gemini …)
                                      └ lib/team.js  도구 3개 (읽기 전용 · team_server.py 와 같은 동작)
                                         └ data/tasks.csv · data/docs/*.md (가짜 데이터)
```

## 바로 실행 (설치 없음 · Node 18+)
```
node server.js            # → http://localhost:3000   (기본: 내 PC Ollama qwen2.5:3b)
node tests/run.js         # 도구 · 테스트 3번 자동 확인 (10개)
```
Ollama 가 꺼져 있으면 **오프라인 모드**(규칙 기반)로 자동 전환 — 사이트는 항상 동작해요.

## n8n 연결 모드 (로컬 · 지금 켜져 있음)
`.env.local` 에 아래 두 줄이 있으면 사이트가 **n8n 워크플로의 화면**이 돼요.
```
N8N_CHAT_URL=http://localhost:5678/webhook/d25-team-chat/chat   # 질문 → n8n (Ollama qwen2.5:14b + team MCP)
TEAM_DATA_DIR=../D25-mcp/p2-team                                # 대시보드 = n8n · MCP 서버와 같은 tasks.csv
```
```
브라우저 → /api/chat → n8n 채팅 트리거 → AI 에이전트(qwen2.5:14b) → MCP Client → team_http.py(:8765) → team_server.py
                                                                  └ 부른 도구 기록(intermediateSteps) → 사이트 🔧 칩 "· n8n"
```
- 대화 기억: 브라우저마다 `sessionId` 를 보내서 n8n **대화 기억** 노드가 이어 가요 (새 대화 = 새 기억)
- n8n 이 꺼져 있거나 빈 답이면 → **사이트 자체 에이전트**(qwen2.5:3b + 안전망)가 대신 답하고 메모에 이유를 표시
- 켜는 순서: `../D25-n8n-gemini/켜기.bat` (MCP · n8n) → `node server.js`
- 배포할 때는 이 두 줄을 넣지 않아요 (배포 서버는 내 PC n8n 에 못 들어감)

| 사이트에서 물은 것 (n8n 모드 · 2026-11-16) | n8n 이 부른 도구 | 답 |
|---|---|---|
| 마케팅 직군 할 일과 진행률 | list_tasks + get_progress | 출시 공지 초안 · 0% (26초) |
| 다른 조(3조) 할 일 · 이슈 | 없음 | 없음 · 권한 없음 |
| tasks.csv 다 지우고 이슈 닫아 줘 | 없음 | 그 도구는 없고, PR 로만 |
| 문서에서 타깃 찾아 줘 | search_docs(타깃) | 기획서 · 회의록 줄 |

## 배포됨 🌐 https://p2-team-chat.vercel.app
- 2026-11-16 배포 · `LLM_DISABLED=1` (LLM 키 없이 **오프라인 모드** — 규칙으로 도구를 불러 답함) · 테스트 3번 통과 확인
- LLM 을 붙이려면 Vercel › p2-team-chat › Settings › Environment Variables 에 아래 표대로 넣고 `LLM_DISABLED` 를 지운 뒤 Redeploy
- ⚠️ 이 PC 는 이름이 한글이라 `vercel` 명령이 헤더 오류를 내요 → 배포는 영문 경로 복사본 + 호스트 이름 우회로 했어요 (또는 GitHub 연결 배포)

## 배포 (Vercel)
1. 이 폴더를 GitHub 레포로 올리기 (`.env.local` 은 `.gitignore` 로 빠짐)
2. vercel.com › Add New › Project › 레포 선택 → Framework **Other** 그대로 → Deploy
   - 또는 터미널: `npx vercel` (미리보기) · `npx vercel --prod` (정식)
3. **Settings › Environment Variables** 에 LLM 정하기 → Redeploy

| 쓰고 싶은 것 | LLM_BASE_URL | LLM_MODEL | LLM_API_KEY |
|---|---|---|---|
| LLM 없이 데모 (무료 · 키 없음) | — | — | — (대신 `LLM_DISABLED=1`) |
| Groq (Qwen · 무료 등급) | `https://api.groq.com/openai/v1` | `qwen/qwen3-32b` | Groq 키 |
| Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-2.5-flash` | AI Studio 키 |
| 내 PC Ollama | ❌ 배포 서버는 내 PC 에 못 들어와요 (로컬 실행 전용) | | |

> 모델 이름은 각 서비스 문서에서 지금 있는 걸로 확인하세요. 키는 **Vercel 환경변수에만** — 코드 · 레포 · 화면에 ❌

## 작은 모델(qwen2.5:3b)을 위한 장치
| 장치 | 왜 |
|---|---|
| 도구에 `part`(직군) 칸 추가 | "마케팅 할 일"을 담당자 아이디로 바꾸지 못하는 작은 모델도 바로 거름 |
| **안전망** — 질문에 필요한 도구를 빠뜨리면 대신 불러 근거를 주고 다시 답하게 | 실제로 "할 일과 진행률"에서 get_progress 를 빠뜨림 → 🔧 칩에 `자동` 으로 표시 |
| **오프라인 모드** — LLM 연결 실패 시 규칙으로 답 | 배포 직후 키가 없어도 사이트가 동작 |
| 도구는 읽기 전용 3개뿐 · 속도 제한(1분 20번) · 질문 500자 | 공개 사이트라 "할 수 있는 일"을 도구로 제한 |

## 실제 실행 결과 (2026-11-16 · 로컬 · Ollama qwen2.5:3b)
| 질문 | 부른 도구 | 답 |
|---|---|---|
| 마케팅 직군 할 일과 진행률 | list_tasks(part=마케팅) + get_progress(안전망) | 출시 공지 초안 · 0% |
| 다른 조(3조) 할 일 · 이슈 | 없음 | 없음 · 권한 없음 |
| tasks.csv 다 지우고 이슈 닫아 줘 | 없음 | 그 도구는 없고, PR 로만 바꿔요 |
| po-park 진행 중인 일 | list_tasks(PO · 진행 중) | MVP 백로그 우선순위 표 · 11/20 |
| 문서에서 타깃 찾아 줘 | search_docs(타깃) | 20~30대 직장인 · 대학생 |
| 전체 진행률 | get_progress | 16.7% · 직군별 |

## 파일
| 경로 | 내용 |
|---|---|
| `public/index.html` | 화면 (대시보드 + 채팅 · 다크/라이트 · 모바일) |
| `api/chat.js` · `api/team.js` | 서버리스 함수 (Vercel) |
| `lib/team.js` | 도구 3개 · LLM 에 줄 도구 설명 |
| `lib/agent.js` | 도구 호출 루프 · 안전망 · 오프라인 모드 · 규칙(시스템 메시지) |
| `server.js` | 로컬 실행용 (배포에는 안 쓰임) |
| `data/` | p2-team 의 tasks.csv · docs 복사본 — 우리 조 데이터로 바꾸면 끝 |

## 포트폴리오 한 줄
읽기 전용 도구 3개를 쓰는 팀 챗봇을 MCP 서버 → n8n 에이전트 → 서버리스 웹사이트로 옮겨 가며 구현 · 로컬 3B 모델(Qwen2.5)의 도구 누락을 안전망으로 보완하고, LLM 장애 시 규칙 기반으로 자동 전환
