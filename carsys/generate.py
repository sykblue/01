"""자동차 예약 시스템 더미 데이터 생성기.

실행: python generate.py
결과: data/cars.csv · customers.csv · branches.csv · reservations.csv (예약 200건) + seed.sql
모든 데이터는 가짜예요. 같은 SEED면 항상 같은 데이터가 나와요.
"""
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 25
N_RESERVATIONS = 200
N_CUSTOMERS = 80
N_CARS = 40
TODAY = date(2026, 11, 17)

random.seed(SEED)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

# ---------- 지점 ----------
branches = [
    {"branch_id": 1, "name": "서울역점", "city": "서울", "phone": "02-0000-0001"},
    {"branch_id": 2, "name": "강남점", "city": "서울", "phone": "02-0000-0002"},
    {"branch_id": 3, "name": "김포공항점", "city": "서울", "phone": "02-0000-0003"},
    {"branch_id": 4, "name": "부산역점", "city": "부산", "phone": "051-000-0004"},
    {"branch_id": 5, "name": "제주공항점", "city": "제주", "phone": "064-000-0005"},
    {"branch_id": 6, "name": "대전역점", "city": "대전", "phone": "042-000-0006"},
]

# ---------- 차량 ----------
# (제조사, 모델, 차종, 연료, 좌석, 1일 요금)
MODELS = [
    ("현대", "아반떼", "준중형", "가솔린", 5, 55000),
    ("현대", "쏘나타", "중형", "하이브리드", 5, 75000),
    ("현대", "그랜저", "대형", "하이브리드", 5, 110000),
    ("현대", "아이오닉5", "중형", "전기", 5, 95000),
    ("현대", "캐스퍼", "경차", "가솔린", 4, 40000),
    ("현대", "스타리아", "승합", "디젤", 11, 140000),
    ("기아", "모닝", "경차", "가솔린", 4, 38000),
    ("기아", "K5", "중형", "가솔린", 5, 72000),
    ("기아", "K8", "대형", "하이브리드", 5, 105000),
    ("기아", "EV6", "중형", "전기", 5, 98000),
    ("기아", "카니발", "승합", "디젤", 9, 130000),
    ("기아", "쏘렌토", "SUV", "하이브리드", 7, 115000),
    ("제네시스", "G80", "대형", "가솔린", 5, 160000),
    ("제네시스", "GV70", "SUV", "가솔린", 5, 150000),
    ("테슬라", "Model Y", "SUV", "전기", 5, 135000),
    ("KG모빌리티", "토레스", "SUV", "가솔린", 5, 85000),
]
COLORS = ["흰색", "검정", "회색", "은색", "파랑", "빨강"]
HANGUL_PLATE = "가나다라마거너더러머버서어저고노도로모보소오조구누두루무부수우주하허호"

cars = []
used_plates = set()
for i in range(1, N_CARS + 1):
    maker, model, ctype, fuel, seats, rate = random.choice(MODELS)
    while True:
        plate = f"{random.randint(10, 399)}{random.choice(HANGUL_PLATE)} {random.randint(1000, 9999)}"
        if plate not in used_plates:
            used_plates.add(plate)
            break
    cars.append({
        "car_id": i,
        "plate": plate,
        "maker": maker,
        "model": model,
        "car_type": ctype,
        "fuel": fuel,
        "seats": seats,
        "year": random.randint(2021, 2026),
        "color": random.choice(COLORS),
        "daily_rate": rate,
        "branch_id": random.choice(branches)["branch_id"],
        "mileage_km": random.randint(3000, 90000),
        "status": "정비중" if random.random() < 0.08 else "운행가능",
    })

# ---------- 고객 ----------
LAST = list("김이박최정강조윤장임한오서신권황안송류홍")
FIRST = ["민준", "서연", "도윤", "지우", "하준", "서윤", "시우", "하은", "주원", "지민",
         "예준", "수아", "건우", "지유", "현우", "채원", "우진", "다은", "선우", "예린",
         "유준", "소율", "정우", "윤서", "승현", "가은", "태윤", "나연", "민재", "하린"]
GRADES = [("일반", 0.6), ("실버", 0.25), ("골드", 0.12), ("VIP", 0.03)]

customers = []
for i in range(1, N_CUSTOMERS + 1):
    birth = date(random.randint(1965, 2004), random.randint(1, 12), random.randint(1, 28))
    customers.append({
        "customer_id": i,
        "name": random.choice(LAST) + random.choice(FIRST),
        "phone": f"010-0000-{i:04d}",              # 가짜 번호 (0000 대역)
        "email": f"user{i:03d}@example.com",        # 예시용 도메인
        "birth_date": birth.isoformat(),
        "license_type": random.choices(["1종 보통", "2종 보통", "1종 대형"], [0.55, 0.4, 0.05])[0],
        "grade": random.choices([g for g, _ in GRADES], [w for _, w in GRADES])[0],
        "joined_at": (TODAY - timedelta(days=random.randint(10, 900))).isoformat(),
    })

# ---------- 예약 ----------
INSURANCE = [("기본", 0), ("일반자차", 15000), ("완전자차", 30000)]
OPTIONS = ["", "", "", "카시트", "내비게이션", "스노우체인", "카시트+내비게이션"]
OPTION_FEE = {"": 0, "카시트": 10000, "내비게이션": 5000, "스노우체인": 8000, "카시트+내비게이션": 15000}
PAYMENT = ["카드", "카드", "카드", "계좌이체", "간편결제", "간편결제"]
GRADE_DISCOUNT = {"일반": 0.0, "실버": 0.05, "골드": 0.10, "VIP": 0.15}

reservations = []
booked = {c["car_id"]: [] for c in cars}   # 같은 차가 같은 날짜에 두 번 잡히지 않게
for i in range(1, N_RESERVATIONS + 1):
    cust = random.choice(customers)
    while True:
        car = random.choice(cars)
        start = TODAY + timedelta(days=random.randint(-120, 60))
        days = random.choices([1, 2, 3, 4, 5, 7, 10, 14], [20, 25, 20, 10, 10, 8, 4, 3])[0]
        end = start + timedelta(days=days)
        if all(end <= s or start >= e for s, e in booked[car["car_id"]]):
            booked[car["car_id"]].append((start, end))
            break
    pickup_hour = random.choice([8, 9, 10, 11, 13, 14, 15, 17, 18])
    booked_at = datetime.combine(start, datetime.min.time()) - timedelta(
        days=random.randint(1, 45), hours=random.randint(0, 23), minutes=random.randint(0, 59))

    if end < TODAY:
        status = random.choices(["반납완료", "취소", "노쇼"], [85, 12, 3])[0]
    elif start <= TODAY <= end:
        status = random.choices(["이용중", "취소"], [92, 8])[0]
    else:
        status = random.choices(["예약확정", "결제대기", "취소"], [75, 15, 10])[0]

    ins_name, ins_fee = random.choice(INSURANCE)
    option = random.choice(OPTIONS)
    base = car["daily_rate"] * days
    discount = int(base * GRADE_DISCOUNT[cust["grade"]])
    total = base - discount + (ins_fee + OPTION_FEE[option]) * days
    return_branch = car["branch_id"] if random.random() < 0.85 else random.choice(branches)["branch_id"]

    reservations.append({
        "reservation_id": f"R{start:%y%m}-{i:04d}",
        "customer_id": cust["customer_id"],
        "car_id": car["car_id"],
        "pickup_branch_id": car["branch_id"],
        "return_branch_id": return_branch,
        "pickup_at": f"{start.isoformat()} {pickup_hour:02d}:00",
        "return_at": f"{end.isoformat()} {pickup_hour:02d}:00",
        "rental_days": days,
        "insurance": ins_name,
        "options": option,
        "base_price": base,
        "discount": discount,
        "total_price": total,
        "payment_method": "" if status == "결제대기" else random.choice(PAYMENT),
        "status": status,
        "booked_at": booked_at.strftime("%Y-%m-%d %H:%M"),
    })

reservations.sort(key=lambda r: r["pickup_at"])


# ---------- 저장 ----------
def save_csv(name, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:  # 엑셀에서 한글 안 깨지게
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


save_csv("branches.csv", branches)
save_csv("cars.csv", cars)
save_csv("customers.csv", customers)
save_csv("reservations.csv", reservations)


def sql_val(v):
    if isinstance(v, int):
        return str(v)
    if v == "":
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def inserts(table, rows):
    cols = ", ".join(rows[0].keys())
    vals = ",\n".join("  (" + ", ".join(sql_val(v) for v in r.values()) + ")" for r in rows)
    return f"INSERT INTO {table} ({cols}) VALUES\n{vals};\n"


schema = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
with open(Path(__file__).parent / "seed.sql", "w", encoding="utf-8") as f:
    f.write("-- 자동 생성 파일 (python generate.py). 직접 고치지 마세요.\n")
    f.write(schema + "\n")
    for t, rows in [("branches", branches), ("cars", cars), ("customers", customers), ("reservations", reservations)]:
        f.write(inserts(t, rows) + "\n")

from collections import Counter
print(f"지점 {len(branches)} · 차량 {len(cars)} · 고객 {len(customers)} · 예약 {len(reservations)}")
print("예약 상태:", dict(Counter(r["status"] for r in reservations)))
