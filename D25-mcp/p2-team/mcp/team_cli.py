"""MCP 없이 쓰는 우리 조 도구 — team_server.py 와 같은 함수를 명령줄로 실행해요.

MCP 를 지원하지 않는 AI 나 사람이 직접 쓸 때:
  python mcp/team_cli.py tasks [--owner dev-kim] [--status "진행 중"]
  python mcp/team_cli.py progress
  python mcp/team_cli.py docs 타깃

차이: MCP 는 AI 가 "언제 어떤 도구를 쓸지" 스스로 고르지만, CLI 는 사람이(또는 셸을 쓰는 AI 가) 직접 불러요.
여기도 읽기 전용 — 쓰기 · 지우기 명령은 없어요.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import team_server as ts  # noqa: E402  (mcp 패키지가 없어도 함수는 동작)


def main(argv=None):
    p = argparse.ArgumentParser(description="우리 조 도구 (읽기 전용 · MCP 없이)")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tasks", help="할 일 보기")
    t.add_argument("--owner", default="", help="담당자 깃허브 아이디")
    t.add_argument("--status", default="", help='"할 일" · "진행 중" · "완료"')
    sub.add_parser("progress", help="직군별 · 전체 진행률")
    d = sub.add_parser("docs", help="docs/*.md 에서 키워드 찾기")
    d.add_argument("keyword")
    a = p.parse_args(argv)
    if a.cmd == "tasks":
        out = ts.할일_보기(owner=a.owner, status=a.status)
    elif a.cmd == "progress":
        out = ts.진행률()
    else:
        out = ts.문서_찾기(keyword=a.keyword)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
