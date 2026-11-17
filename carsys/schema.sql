-- 자동차 예약 시스템 테이블 (PostgreSQL · Supabase)
create table if not exists branches (
  branch_id   int primary key,
  name        text not null,
  city        text not null,
  phone       text
);

create table if not exists cars (
  car_id      int primary key,
  plate       text unique not null,
  maker       text not null,
  model       text not null,
  car_type    text not null,              -- 경차 · 준중형 · 중형 · 대형 · SUV · 승합
  fuel        text not null,              -- 가솔린 · 디젤 · 하이브리드 · 전기
  seats       int not null,
  year        int not null,
  color       text,
  daily_rate  int not null,               -- 1일 요금(원)
  branch_id   int references branches(branch_id),
  mileage_km  int,
  status      text not null default '운행가능'  -- 운행가능 · 정비중
);

create table if not exists customers (
  customer_id  int primary key,
  name         text not null,
  phone        text,
  email        text,
  birth_date   date,
  license_type text,
  grade        text default '일반',        -- 일반 · 실버 · 골드 · VIP
  joined_at    date
);

create table if not exists reservations (
  reservation_id   text primary key,
  customer_id      int references customers(customer_id),
  car_id           int references cars(car_id),
  pickup_branch_id int references branches(branch_id),
  return_branch_id int references branches(branch_id),
  pickup_at        timestamp not null,
  return_at        timestamp not null,
  rental_days      int not null,
  insurance        text,                  -- 기본 · 일반자차 · 완전자차
  options          text,
  base_price       int not null,
  discount         int not null default 0,
  total_price      int not null,
  payment_method   text,
  status           text not null,         -- 결제대기 · 예약확정 · 이용중 · 반납완료 · 취소 · 노쇼
  booked_at        timestamp
);
