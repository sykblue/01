// 로컬 실행용 — npm 설치 없이 `node server.js` → http://localhost:3000
// 배포(Vercel)에서는 이 파일 대신 api/*.js 가 서버리스 함수로, public/ 이 정적 파일로 올라가요.
const http = require("http");
const fs = require("fs");
const path = require("path");

// .env.local 이 있으면 읽기 (LLM_BASE_URL · LLM_MODEL · LLM_API_KEY)
for (const f of [".env.local", ".env"]) {
  const p = path.join(__dirname, f);
  if (!fs.existsSync(p)) continue;
  for (const line of fs.readFileSync(p, "utf8").split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$/);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
}

const routes = { "/api/chat": require("./api/chat"), "/api/team": require("./api/team") };
const PUB = path.join(__dirname, "public");
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon" };
const PORT = Number(process.env.PORT || 3000);
// 내 PC 에선 127.0.0.1(나만), Render 같은 서버에선 0.0.0.0(밖에서 접속) — HOST 로 바꿀 수 있어요
const HOST = process.env.HOST || (process.env.RENDER ? "0.0.0.0" : "127.0.0.1");

http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  const handler = routes[url.pathname];
  if (handler) {
    let raw = "";
    for await (const chunk of req) { raw += chunk; if (raw.length > 50_000) break; }
    try { req.body = raw ? JSON.parse(raw) : {}; } catch { req.body = {}; }
    return handler(req, res);
  }
  const file = path.normalize(path.join(PUB, url.pathname === "/" ? "index.html" : decodeURIComponent(url.pathname)));
  if (!file.startsWith(PUB) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.statusCode = 404; return res.end("not found"); }
  res.setHeader("content-type", TYPES[path.extname(file)] || "application/octet-stream");
  fs.createReadStream(file).pipe(res);
}).listen(PORT, HOST, () => {
  const { CFG } = require("./lib/agent");
  console.log(`우리 조 챗봇 → http://localhost:${PORT}   (LLM: ${CFG.disabled ? "끔 · 오프라인 모드" : CFG.model + " @ " + CFG.baseUrl})`);
});
