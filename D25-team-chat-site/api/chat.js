// POST /api/chat  { message, history: [{role, content}] }  →  { reply, steps, mode, model }
const { chat } = require("../lib/agent");

const hits = new Map(); // 아주 간단한 속도 제한 (IP 당 1분 20번) — 서버리스 인스턴스마다 따로라 '대충'의 보호
function limited(ip) {
  const now = Date.now(), win = 60_000, max = 20;
  const arr = (hits.get(ip) || []).filter((t) => now - t < win);
  arr.push(now);
  hits.set(ip, arr);
  return arr.length > max;
}

function send(res, code, obj) {
  res.statusCode = code;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.setHeader("cache-control", "no-store");
  res.end(JSON.stringify(obj));
}

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "POST 만 돼요" });
  const ip = String(req.headers["x-forwarded-for"] || req.socket?.remoteAddress || "?").split(",")[0].trim();
  if (limited(ip)) return send(res, 429, { error: "잠깐만요 — 1분에 20번까지예요" });
  let body = req.body;
  if (typeof body === "string") { try { body = JSON.parse(body); } catch { body = {}; } }
  const message = String(body?.message || "").trim();
  if (!message) return send(res, 400, { error: "message 가 비었어요" });
  if (message.length > 500) return send(res, 400, { error: "500자까지만 보낼 수 있어요" });
  const history = Array.isArray(body?.history) ? body.history.slice(-8) : [];
  try {
    send(res, 200, await chat({ message, history, sessionId: String(body?.sessionId || "") }));
  } catch (e) {
    send(res, 500, { error: "서버 오류", detail: String(e.message || e).slice(0, 200) });
  }
};
