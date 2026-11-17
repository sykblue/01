"""사내 공용차 20대 엑셀(carlist.xlsx) + 시트별 CSV 더미 데이터 생성기.

실행: python make_carlist.py
실제 엑셀처럼 사람이 손으로 적은 흔적(빈칸 · 날짜 형식 섞임 · 오타)을 일부러 몇 군데 넣었어요.
모든 데이터는 가짜예요.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

random.seed(1117)
HERE = Path(__file__).parent
NOW = datetime(2026, 11, 17, 15, 0)

# ---------- 직원 ----------
staff = [
    ("김민준", "영업팀"), ("이서연", "영업팀"), ("박도윤", "영업팀"), ("최지우", "마케팅팀"),
    ("정하준", "마케팅팀"), ("강서윤", "개발팀"), ("조시우", "개발팀"), ("윤하은", "경영지원팀"),
    ("장주원", "경영지원팀"), ("임지민", "고객지원팀"), ("한예준", "고객지원팀"), ("오수아", "영업팀"),
]
staff_rows = [[n, d, f"010-0000-{i:04d}", f"staff{i:02d}@example.com"] for i, (n, d) in enumerate(staff, 1)]

# ---------- 차량 ----------
MODELS = [("아반떼", "가솔린"), ("쏘나타", "하이브리드"), ("K5", "가솔린"), ("아이오닉5", "전기"),
          ("EV6", "전기"), ("스포티지", "디젤"), ("카니발", "디젤"), ("스타리아", "디젤"),
          ("레이", "가솔린"), ("그랜저", "하이브리드")]
PLACES = ["본사 B2", "본사 B3", "물류센터", "판교 지점"]
H = "가나다라마거너더러머버서어저고노도로모보소오조구누두루무부수우주"

cars = []
used = set()
for i in range(20):
    model, fuel = MODELS[i % len(MODELS)]
    while True:
        plate = f"{random.randint(12, 399)}{random.choice(H)} {random.randint(1000, 9999)}"
        if plate not in used:
            used.add(plate)
            break
    cars.append({"plate": plate, "model": model, "fuel": fuel, "year": random.randint(2020, 2025),
                 "km": random.randint(8000, 85000), "place": random.choice(PLACES), "status": "대기", "memo": ""})
cars[7]["status"] = "정비중"
cars[7]["memo"] = "타이어 교체 (11/18 입고 예정)"
cars[15]["status"] = "정비중"
cars[15]["memo"] = "정기점검"

# ---------- 배차기록 ----------
PURPOSE = ["거래처 방문", "현장 점검", "물품 배송", "외부 미팅", "행사 지원", "고객 방문", "은행 업무"]
DEST = ["판교", "강남", "인천", "수원", "성수", "여의도", "김포", "분당", "광명", "일산"]
logs = []
avail = [c for c in cars if c["status"] != "정비중"]
t = NOW - timedelta(days=21)
while t < NOW - timedelta(hours=6):
    car = random.choice(avail)
    out_t = t.replace(hour=random.choice([8, 9, 10, 13, 14]), minute=random.choice([0, 10, 20, 30, 40, 50]))
    ret_t = out_t + timedelta(hours=random.randint(1, 7), minutes=random.choice([0, 15, 30, 45]))
    if ret_t > NOW:
        break
    km = random.randint(12, 140)
    out_km = car["km"]
    car["km"] += km
    n, d = random.choice(staff)
    logs.append({"car": car, "user": n, "dept": d, "out": out_t, "ret": ret_t,
                 "out_km": out_km, "ret_km": car["km"], "dest": random.choice(DEST),
                 "purpose": random.choice(PURPOSE), "note": ""})
    t += timedelta(hours=random.choice([1, 2, 3, 5, 18]))

# 지금 사용 중인 차 4대 (반납 칸 비어 있음 = 정상)
for car in random.sample(avail, 4):
    n, d = random.choice(staff)
    out_t = NOW - timedelta(hours=random.randint(1, 5), minutes=random.choice([0, 20, 40]))
    logs.append({"car": car, "user": n, "dept": d, "out": out_t, "ret": None, "out_km": car["km"],
                 "ret_km": None, "dest": random.choice(DEST), "purpose": random.choice(PURPOSE), "note": ""})
    car["status"] = "사용중"

logs.sort(key=lambda r: r["out"])


def fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


log_rows = []
for i, r in enumerate(logs, 1):
    log_rows.append([i, r["car"]["plate"], r["user"], r["dept"], fmt(r["out"]), fmt(r["ret"]),
                     r["out_km"], r["ret_km"] if r["ret_km"] is not None else "", r["dest"], r["purpose"], r["note"]])

# ---------- 사람이 손으로 적은 흔적 (일부러 넣는 이상한 값) ----------
done = [row for row in log_rows if row[5]]
anomalies = []
# 1) 날짜 형식이 다른 값
done[3][4] = done[3][4].replace("-", ".")                         # 2026.11.01 09:30
anomalies.append(f"배차기록 {done[3][0]}번 출차일시: 점(.) 형식")
d = datetime.strptime(done[8][5], "%Y-%m-%d %H:%M")
done[8][5] = f"{d.month}/{d.day} {d.hour}시"                       # 11/3 15시
anomalies.append(f"배차기록 {done[8][0]}번 반납일시: '월/일 시' 형식")
d = datetime.strptime(done[15][4], "%Y-%m-%d %H:%M")
done[15][4] = f"{d.month}월 {d.day}일 오{'전' if d.hour < 12 else '후'} {d.hour if d.hour <= 12 else d.hour - 12}시"
anomalies.append(f"배차기록 {done[15][0]}번 출차일시: '11월 n일 오전 n시' 형식")
# 2) 반납했는데 반납 주행거리 빈칸
done[20][7] = ""
done[20][10] = "주행거리 적는 걸 깜빡함"
anomalies.append(f"배차기록 {done[20][0]}번: 반납일시는 있는데 반납km 빈칸")
# 3) 반납km가 출차km보다 작음 (자리 하나 빠뜨림)
done[27][7] = int(str(done[27][7])[:-1])
anomalies.append(f"배차기록 {done[27][0]}번: 반납km < 출차km (숫자 하나 빠짐)")
# 4) 차량번호 띄어쓰기 없이 적음
done[33][1] = done[33][1].replace(" ", "")
anomalies.append(f"배차기록 {done[33][0]}번 차량번호: 띄어쓰기 없음")
# 5) 사용자 이름 빈칸
done[40][2] = ""
anomalies.append(f"배차기록 {done[40][0]}번: 사용자 빈칸")
# 6) km에 단위 붙임
done[45][6] = f"{done[45][6]:,}km"
anomalies.append(f"배차기록 {done[45][0]}번 출차km: '12,345km'처럼 글자로 적음")

car_rows = []
for c in cars:
    car_rows.append([c["plate"], c["model"], c["fuel"], c["year"], c["km"], c["place"], c["status"], c["memo"]])
# 7) 차량목록 상태가 배차기록과 안 맞음 (사용중인데 '대기'로 둠)
in_use_plates = [r[1] for r in log_rows if not r[5]]
for row in car_rows:
    if row[0] == in_use_plates[0]:
        row[6] = "대기"
        anomalies.append(f"차량목록 {row[0]}: 배차기록상 사용 중인데 상태가 '대기'")
        break
# 8) 차량목록 연식 빈칸
car_rows[11][3] = ""
anomalies.append(f"차량목록 {car_rows[11][0]}: 연식 빈칸")

SHEETS = {
    "차량목록": (["차량번호", "차종", "연료", "연식", "현재주행거리(km)", "보관위치", "상태", "메모"], car_rows),
    "배차기록": (["번호", "차량번호", "사용자", "부서", "출차일시", "반납일시", "출차km", "반납km", "목적지", "용도", "비고"], log_rows),
    "직원": (["이름", "부서", "연락처", "이메일"], staff_rows),
}

# ---------- xlsx ----------
wb = Workbook()
wb.remove(wb.active)
head_fill = PatternFill("solid", fgColor="DDEBF7")
for name, (cols, rows) in SHEETS.items():
    ws = wb.create_sheet(name)
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = head_fill
    for r in rows:
        ws.append(r)
    for i, col in enumerate(cols, 1):
        width = max(len(str(col)), *(len(str(r[i - 1])) for r in rows)) * 1.7 + 2
        ws.column_dimensions[get_column_letter(i)].width = min(width, 40)
    ws.freeze_panes = "A2"
wb.save(HERE / "carlist.xlsx")

# ---------- csv (시트별) ----------
for name, (cols, rows) in SHEETS.items():
    with open(HERE / f"carlist_{name}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)

with open(HERE / "넣어둔_이상한값.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(anomalies) + "\n")
print(f"차량 {len(car_rows)} · 배차기록 {len(log_rows)} · 직원 {len(staff_rows)} · 이상한 값 {len(anomalies)}")
