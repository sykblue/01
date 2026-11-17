-- create_carsystem_schema · 공용차 배차판 (PRD.md 6. 기술 기준)

-- 1) 차량 20대
create table public.cars (
  plate       text primary key,                       -- 차량번호 '247라 5929'
  model       text not null,
  fuel        text not null,
  year        int,                                    -- 엑셀에 빈칸 1곳이 있어 비워 둘 수 있게
  mileage_km  int  not null check (mileage_km >= 0),  -- 현재 주행거리 (반납하면 자동 갱신)
  place       text,
  in_repair   boolean not null default false,         -- 정비중이면 빌릴 수 없음 (R5)
  memo        text
);

-- 2) 직원 12명
create table public.staff (
  name  text primary key,
  dept  text not null
);

-- 3) 대여대장 (운행 기록) · 지우거나 고치지 않고 더하기만 (R8)
create table public.trips (
  id        bigint generated always as identity primary key,
  plate     text not null references public.cars(plate),
  user_name text references public.staff(name),
  dept      text,
  dest      text,
  purpose   text,
  out_at    timestamptz not null default now(),
  out_km    int not null check (out_km >= 0),
  ret_at    timestamptz,                -- 비어 있으면 = 지금 사용 중 (R3)
  ret_km    int,
  ret_by    text,                       -- 반납한 사람 (R6)
  note      text,
  -- R4: 반납 시각과 반납km는 함께 있거나 함께 없어야 함
  constraint trips_return_pair check ((ret_at is null) = (ret_km is null)),
  -- R4: 반납km는 출차km 이상
  constraint trips_km_order   check (ret_km is null or ret_km >= out_km),
  constraint trips_time_order check (ret_at is null or ret_at >= out_at)
);

-- R1: 같은 차에 "반납 안 된 기록"은 하나만 → 이미 사용 중인 차는 못 빌림
create unique index trips_one_open_per_car on public.trips (plate) where ret_at is null;
create index trips_user_idx on public.trips (user_name, out_at desc);

-- R5: 정비중인 차는 빌릴 수 없음
create or replace function public.block_repair_car()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if exists (select 1 from public.cars c where c.plate = new.plate and c.in_repair) then
    raise exception '정비중인 차는 빌릴 수 없어요: %', new.plate;
  end if;
  return new;
end $$;

create trigger trips_block_repair
  before insert on public.trips
  for each row execute function public.block_repair_car();

-- F4: 반납하면 차의 현재 주행거리를 반납km로 갱신
create or replace function public.sync_car_mileage()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.ret_km is not null and (old.ret_km is null) then
    update public.cars set mileage_km = greatest(mileage_km, new.ret_km) where plate = new.plate;
  end if;
  return new;
end $$;

create trigger trips_sync_mileage
  after update of ret_km on public.trips
  for each row execute function public.sync_car_mileage();

revoke execute on function public.block_repair_car() from public, anon, authenticated;
revoke execute on function public.sync_car_mileage() from public, anon, authenticated;

-- R3: 상태는 적지 않고 계산 (대기 · 사용 중 · 정비중)
create view public.car_status with (security_invoker = true) as
select c.*,
       case when t.id is not null then '사용 중'
            when c.in_repair     then '정비중'
            else '대기' end as status,
       t.id as trip_id, t.user_name, t.dept, t.dest, t.out_at
from public.cars c
left join public.trips t on t.plate = c.plate and t.ret_at is null;

-- 보안 (RLS): 로그인 없는 사내용 → 읽기 · 빌리기 · 반납만 허용, 삭제는 아무도 못 함
alter table public.cars  enable row level security;
alter table public.staff enable row level security;
alter table public.trips enable row level security;

create policy "누구나 차량 보기" on public.cars  for select to anon, authenticated using (true);
create policy "누구나 직원 보기" on public.staff for select to anon, authenticated using (true);
create policy "누구나 기록 보기" on public.trips for select to anon, authenticated using (true);
create policy "빌리기 = 새 기록 (반납 전 상태로만)" on public.trips for insert to anon, authenticated
  with check (ret_at is null and ret_km is null);
create policy "반납 = 사용 중인 기록만 수정" on public.trips for update to anon, authenticated
  using (ret_at is null) with check (ret_at is not null and ret_km is not null);

-- 칸 단위 권한: 화면(anon)은 차량 · 직원을 고칠 수 없고, 반납 때는 반납 칸 4개만 고칠 수 있음
revoke insert, update, delete, truncate on public.cars, public.staff, public.trips from anon, authenticated;
grant insert (plate, user_name, dept, dest, purpose, out_km, note) on public.trips to anon, authenticated;
grant update (ret_at, ret_km, ret_by, note) on public.trips to anon, authenticated;

-- F5: 실시간 반영
alter publication supabase_realtime add table public.trips, public.cars;
