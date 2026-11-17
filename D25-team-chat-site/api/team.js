// GET /api/team  →  대시보드용 { tasks, progress, model }  (읽기 전용)
const team = require("../lib/team");
const { CFG } = require("../lib/agent");

module.exports = (req, res) => {
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.setHeader("cache-control", "no-store");
  if (req.method !== "GET") { res.statusCode = 405; return res.end(JSON.stringify({ error: "GET 만 돼요" })); }
  res.end(JSON.stringify({
    tasks: team.listTasks(),
    progress: team.getProgress(),
    model: CFG.n8nUrl ? "n8n 워크플로" : CFG.disabled ? null : CFG.model,
    source: CFG.n8nUrl ? "n8n" : "site",
  }));
};
