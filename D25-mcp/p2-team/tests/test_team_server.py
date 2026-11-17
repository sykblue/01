"""team_server.py 검증 체크 (조 과제 4-2) 를 자동으로 확인하는 테스트.

실행:  python -m unittest discover -s tests -v      (p2-team 폴더에서)
mcp 패키지가 없어도 도구 함수 자체는 시험할 수 있어요.
"""
import ast
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "mcp", "team_server.py")
sys.path.insert(0, os.path.join(ROOT, "mcp"))
import team_server as ts  # noqa: E402


class 검증체크(unittest.TestCase):
    def test_1_쓰기_지우기_코드가_없다(self):
        with open(SERVER, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = ast.unparse(node.func)
                self.assertNotIn(name, {"os.remove", "os.unlink", "shutil.rmtree", "os.rename", "csv.writer"}, name)
                if name == "open" and len(node.args) > 1:
                    mode = ast.literal_eval(node.args[1]) if isinstance(node.args[1], ast.Constant) else "?"
                    self.assertNotRegex(str(mode), "[wax+]", "쓰기 모드 open 발견")
                for kw in node.keywords:
                    if name == "open" and kw.arg == "mode":
                        self.assertNotRegex(str(ast.literal_eval(kw.value)), "[wax+]")

    def test_2_경로가_파일_위치_기준(self):
        cwd = os.getcwd()
        try:
            os.chdir(os.path.expanduser("~"))   # 다른 곳에서 실행해도
            self.assertEqual(len(ts.할일_보기()), 6)  # 같은 tasks.csv 를 읽는다
        finally:
            os.chdir(cwd)

    def test_3_도구_3개_등록(self):
        if ts.FastMCP is None:
            self.skipTest("mcp 미설치 — pip install mcp 후 다시")
        import asyncio
        tools = asyncio.run(ts.mcp.list_tools())
        self.assertEqual(sorted(t.name for t in tools), sorted(["list_tasks", "get_progress", "search_docs"]))
        self.assertEqual(sorted(t.title for t in tools), sorted(["할일_보기", "진행률", "문서_찾기"]))
        for t in tools:
            self.assertRegex(t.name, r"^[A-Za-z0-9_.-]+$")  # MCP 도구 이름 표준(SEP-986)
            self.assertGreater(len(t.description or ""), 20, t.name + " 설명이 너무 짧음")
            ann = t.annotations
            ro = getattr(ann, "read_only_hint", None) if ann else None
            ro = ro if ro is not None else (getattr(ann, "readOnlyHint", None) if ann else None)
            self.assertTrue(ro, t.name + " 에 읽기 전용 표시가 없음")
            # Claude 는 입력 칸 이름이 영문 · 숫자 · _ · - · . 가 아니면 도구를 못 써요 (실제 실행에서 발견)
            for prop in ((t.input_schema if hasattr(t, "input_schema") else t.inputSchema) or {}).get("properties", {}):
                self.assertRegex(prop, r"^[A-Za-z0-9_.-]{1,64}$", t.name + " 입력 칸 이름: " + prop)

    def test_4_없는_담당자는_빈_목록(self):
        self.assertEqual(ts.할일_보기(owner="없는-사람"), [])
        self.assertEqual(ts.할일_보기(status="없는상태"), [])

    def test_5_설명만_읽어도_안다(self):
        for f in (ts.할일_보기, ts.진행률, ts.문서_찾기):
            self.assertIn("읽기 전용", f.__doc__)


class 동작(unittest.TestCase):
    def test_거르기(self):
        self.assertEqual([r["번호"] for r in ts.할일_보기(owner="dev-kim")], ["1", "2"])
        self.assertEqual([r["번호"] for r in ts.할일_보기(status="진행 중")], ["1", "5"])

    def test_진행률(self):
        p = ts.진행률()
        self.assertEqual(p["전체"], {"완료": 1, "전체": 6, "진행률": 16.7})
        self.assertEqual(p["직군별"]["PO"]["진행률"], 50.0)

    def test_문서_찾기(self):
        hits = ts.문서_찾기("타깃")
        self.assertTrue(hits and all(h["파일"].startswith("docs/") for h in hits))
        self.assertLessEqual(len(ts.문서_찾기("e")), ts.MAX_HITS)
        self.assertEqual(ts.문서_찾기(""), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
