// 우리 조 도구 3개 — p2-team/mcp/team_server.py 와 같은 동작을 JS 로 옮긴 것 (읽기 전용)
// 쓰기 · 지우기 함수는 일부러 없어요. 데이터는 data/tasks.csv · data/docs/*.md (가짜 데이터)
const fs = require("fs");
const path = require("path");

// TEAM_DATA_DIR 를 주면 그 폴더(예: ../D25-mcp/p2-team)의 tasks.csv · docs 를 읽어요 — n8n · MCP 서버와 같은 데이터
const DATA = process.env.TEAM_DATA_DIR
  ? path.resolve(__dirname, "..", process.env.TEAM_DATA_DIR)
  : path.join(__dirname, "..", "data");
const TASKS = path.join(DATA, "tasks.csv");
const DOCS = path.join(DATA, "docs");
const MAX_HITS = 30;
const STATES = ["할 일", "진행 중", "완료"];

function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') q = false;
      else cell += c;
    } else if (c === '"') q = true;
    else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cell); rows.push(row); row = []; cell = "";
    } else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows.filter((r) => r.some((x) => x.trim()));
}

function readTasks() {
  if (!fs.existsSync(TASKS)) return [];
  const text = fs.readFileSync(TASKS, "utf8").replace(/^﻿/, "");
  const [head, ...rows] = parseCsv(text);
  if (!head) return [];
  const keys = head.map((k) => k.trim());
  return rows.map((r) => Object.fromEntries(keys.map((k, i) => [k, (r[i] || "").trim()])));
}

/** 할 일 보기 — owner(담당자 아이디) · status(상태) · part(직군) 로 거르기 */
function listTasks({ owner = "", status = "", part = "" } = {}) {
  const who = String(owner || "").trim(), st = String(status || "").trim(), pt = String(part || "").trim();
  return readTasks().filter((r) =>
    (!who || r["담당자"] === who) && (!st || r["상태"] === st) && (!pt || r["직군"] === pt));
}

/** 진행률 — 직군별 · 전체 (완료 / 전체 × 100, 소수 첫째 자리) */
function getProgress() {
  const by = {};
  let done = 0, total = 0;
  for (const r of readTasks()) {
    const p = r["직군"] || "미정";
    const d = (by[p] ||= { 완료: 0, 전체: 0 });
    d.전체++; total++;
    if (r["상태"] === "완료") { d.완료++; done++; }
  }
  const pct = (a, b) => (b ? Math.round((a / b) * 1000) / 10 : 0);
  for (const d of Object.values(by)) d.진행률 = pct(d.완료, d.전체);
  return { 전체: { 완료: done, 전체: total, 진행률: pct(done, total) }, 직군별: by };
}

/** 문서 찾기 — docs/*.md 에서 키워드가 있는 줄 (최대 30줄) */
function searchDocs({ keyword = "" } = {}) {
  const word = String(keyword || "").trim().toLowerCase();
  if (!word || !fs.existsSync(DOCS)) return [];
  const hits = [];
  for (const name of fs.readdirSync(DOCS).filter((f) => f.endsWith(".md")).sort()) {
    const lines = fs.readFileSync(path.join(DOCS, name), "utf8").replace(/^﻿/, "").split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toLowerCase().includes(word)) {
        hits.push({ 파일: "docs/" + name, 줄: i + 1, 내용: lines[i].trim() });
        if (hits.length >= MAX_HITS) return hits;
      }
    }
  }
  return hits;
}

const owners = () => [...new Set(readTasks().map((r) => r["담당자"]).filter(Boolean))];
const parts = () => [...new Set(readTasks().map((r) => r["직군"]).filter(Boolean))];

// LLM 에 알려 줄 도구 설명 (OpenAI 호환 tools 형식) — 이름은 MCP 서버와 같음
const TOOL_SPECS = [
  {
    type: "function",
    function: {
      name: "list_tasks",
      description: "우리 조 할 일 목록을 보여 줍니다(읽기 전용). part=직군(개발·디자인·PO·마케팅), owner=담당자 아이디, status=상태(할 일·진행 중·완료). 비우면 전체.",
      parameters: {
        type: "object",
        properties: {
          part: { type: "string", description: "직군: 개발 · 디자인 · PO · 마케팅" },
          owner: { type: "string", description: "담당자 깃허브 아이디 (예: dev-kim)" },
          status: { type: "string", description: "할 일 · 진행 중 · 완료" },
        },
      },
    },
  },
  {
    type: "function",
    function: {
      name: "get_progress",
      description: "직군별 · 전체 진행률을 계산합니다(읽기 전용).",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function",
    function: {
      name: "search_docs",
      description: "우리 조 문서(기획서 · 회의록)에서 키워드가 들어 있는 줄을 찾습니다(읽기 전용).",
      parameters: {
        type: "object",
        properties: { keyword: { type: "string", description: "찾을 낱말 (예: 타깃)" } },
        required: ["keyword"],
      },
    },
  },
];

const TOOLS = { list_tasks: listTasks, get_progress: getProgress, search_docs: searchDocs };

function runTool(name, args) {
  const fn = TOOLS[name];
  if (!fn) return { 오류: `없는 도구: ${name} (쓸 수 있는 도구: list_tasks · get_progress · search_docs)` };
  return fn(args && typeof args === "object" ? args : {});
}

module.exports = { DATA, listTasks, getProgress, searchDocs, readTasks, owners, parts, runTool, TOOL_SPECS, STATES, MAX_HITS };
