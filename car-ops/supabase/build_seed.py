"""carlist.xlsx → 02_seed_carsystem.sql (값 정리 + 고친 내역 출력)."""
import re
import sys
from pathlib import Path

from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
wb = load_workbook(HERE.parent / "carlist.xlsx")
YEAR = 2026
fixes = []


def rows(name):
    r = list(wb[name].iter_rows(values_only=True))
    return [dict(zip(r[0], x)) for x in r[1:]]


def norm_plate(p, where):
    p = str(p).strip()
    m = re.fullmatch(r"(\d{2,3}[가-힣])\s*(\d{4})", p)
    fixed = f"{m.group(1)} {m.group(2)}"
    if fixed != p:
        fixes.append((where, "차량번호", p, fixed, "띄어쓰기 넣음"))
    return fixed


def norm_dt(v, where, col):
    if v in (None, ""):
        return None
    s = str(v).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", s):
        return s
    m = re.fullmatch(r"(\d{4})\.(\d{1,2})\.(\d{1,2}) (\d{1,2}):(\d{2})", s)
    if m:
        y, mo, d, h, mi = map(int, m.groups())
    elif m := re.fullmatch(r"(\d{1,2})/(\d{1,2}) (\d{1,2})시", s):
        y, (mo, d, h), mi = YEAR, map(int, m.groups()), 0
    elif m := re.fullmatch(r"(\d{1,2})월 (\d{1,2})일 오(전|후) (\d{1,2})시", s):
        mo, d, ap, h = int(m[1]), int(m[2]), m[3], int(m[4])
        y, mi = YEAR, 0
        h = h + 12 if ap == "후" and h < 12 else h
    else:
        raise ValueError(f"모르는 날짜 형식: {s}")
    fixed = f"{y}-{mo:02d}-{d:02d} {h:02d}:{mi:02d}"
    fixes.append((where, col, s, fixed, "날짜 형식 통일 (연도 없는 값은 2026년)" if "/" in s or "월" in s else "날짜 형식 통일"))
    return fixed


def norm_km(v, where, col):
    if v in (None, ""):
        return None
    if isinstance(v, int):
        return v
    fixed = int(re.sub(r"[^\d]", "", str(v)))
    fixes.append((where, col, v, fixed, "숫자만 남김"))
    return fixed


cars = rows("차량목록")
staff = rows("직원")
logs = rows("배차기록")

for c in cars:
    c["차량번호"] = norm_plate(c["차량번호"], f"차량목록 {c['차량번호']}")
    if c["연식"] in (None, ""):
        fixes.append((f"차량목록 {c['차량번호']}", "연식", "(빈칸)", "NULL", "모르는 값은 비워 둠"))

for r in logs:
    w = f"배차기록 번호 {r['번호']}"
    r["차량번호"] = norm_plate(r["차량번호"], w)
    r["출차일시"] = norm_dt(r["출차일시"], w, "출차일시")
    r["반납일시"] = norm_dt(r["반납일시"], w, "반납일시")
    r["출차km"] = norm_km(r["출차km"], w, "출차km")
    r["반납km"] = norm_km(r["반납km"], w, "반납km")
    if not r["사용자"]:
        fixes.append((w, "사용자", "(빈칸)", "NULL", "누군지 모름 · 비고에 표시"))
        r["비고"] = ((r["비고"] or "") + " 사용자 미상(엑셀 빈칸)").strip()

# 반납km 빈칸 · 출차km보다 작은 값 → 같은 차의 다음 출차km로 채움
by_car = {}
for r in sorted(logs, key=lambda x: x["출차일시"]):
    by_car.setdefault(r["차량번호"], []).append(r)
for plate, lst in by_car.items():
    km_order = sorted(lst, key=lambda x: x["출차km"])   # 주행거리 순서 = 실제로 탄 순서
    for i, r in enumerate(km_order):
        if not r["반납일시"]:
            continue
        bad = r["반납km"] is None or r["반납km"] < r["출차km"]
        if bad:
            nxt = km_order[i + 1]["출차km"] if i + 1 < len(km_order) else None
            car_km = next(c["현재주행거리(km)"] for c in cars if c["차량번호"] == plate)
            new = nxt if nxt is not None else car_km
            fixes.append((f"배차기록 번호 {r['번호']}", "반납km", r["반납km"] if r["반납km"] is not None else "(빈칸)",
                          new, "같은 차의 다음 출차km로 채움"))
            r["반납km"] = new

# 시트 비교: 차량목록 '상태' 칸은 DB에 넣지 않음 (계산)
open_plates = {r["차량번호"] for r in logs if not r["반납일시"]}
for c in cars:
    actual = "사용중" if c["차량번호"] in open_plates else ("정비중" if c["상태"] == "정비중" else "대기")
    if c["상태"] != actual:
        fixes.append((f"차량목록 {c['차량번호']}", "상태", c["상태"], actual, "상태는 대여대장으로 계산 (넣지 않음)"))

# 점검: 같은 차의 기록이 시간상 겹치지 않는지, km가 이어지는지
warnings = []
for plate, lst in by_car.items():
    for a, b in zip(lst, lst[1:]):
        if not a["반납일시"] or a["반납일시"] > b["출차일시"]:
            warnings.append(f"{plate}: 번호 {a['번호']}({a['출차일시']}~{a['반납일시']}) 반납 전에 "
                            f"번호 {b['번호']}({b['출차일시']}) 출차")
        if a["반납km"] is not None and a["반납km"] > b["출차km"]:
            warnings.append(f"{plate}: 번호 {a['번호']} 반납km {a['반납km']} > 다음 출차km {b['출차km']}")


def q(v):
    if v is None or v == "":
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def ts(v):
    return "null" if v is None else f"'{v}:00+09'"


sql = ["-- 02_seed_carsystem · carlist.xlsx에서 정리한 값 (python build_seed.py)", "begin;", ""]
sql.append("insert into public.staff (name, dept) values")
sql.append(",\n".join(f"  ({q(s['이름'])}, {q(s['부서'])})" for s in staff) + ";\n")
sql.append("insert into public.cars (plate, model, fuel, year, mileage_km, place, in_repair, memo) values")
sql.append(",\n".join(
    f"  ({q(c['차량번호'])}, {q(c['차종'])}, {q(c['연료'])}, {q(c['연식'])}, {c['현재주행거리(km)']}, "
    f"{q(c['보관위치'])}, {q(c['상태'] == '정비중')}, {q(c['메모'])})" for c in cars) + ";\n")
sql.append("-- 대여대장: 엑셀 번호 순서대로 (id 1~99)")
sql.append("insert into public.trips (plate, user_name, dept, dest, purpose, out_at, out_km, ret_at, ret_km, ret_by, note) values")
sql.append(",\n".join(
    f"  ({q(r['차량번호'])}, {q(r['사용자'])}, {q(r['부서'])}, {q(r['목적지'])}, {q(r['용도'])}, "
    f"{ts(r['출차일시'])}, {r['출차km']}, {ts(r['반납일시'])}, {q(r['반납km'])}, "
    f"{q(r['사용자']) if r['반납일시'] else 'null'}, {q(r['비고'])})"
    for r in sorted(logs, key=lambda x: x["번호"])) + ";\n")
sql.append("commit;")
(HERE / "02_seed_carsystem.sql").write_text("\n".join(sql), encoding="utf-8")

print(f"직원 {len(staff)} · 차량 {len(cars)} · 대여대장 {len(logs)} (반납 안 됨 {len(open_plates)})")
print(f"\n시간이 겹치는 기록 {len(warnings)}건:")
for w in warnings:
    print(" ", w)
print("\n고친 값:")
for f in fixes:
    print(" | ".join(map(str, f)))
