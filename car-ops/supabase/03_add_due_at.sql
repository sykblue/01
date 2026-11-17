-- add_trip_due_at · 대여할 때 "반납 예정" 시각 받기
alter table public.trips add column due_at timestamptz;
alter table public.trips add constraint trips_due_after_out check (due_at is null or due_at >= out_at);

-- 화면(anon)이 빌릴 때 due_at도 넣을 수 있게
grant insert (due_at) on public.trips to anon, authenticated;

-- 상태 뷰에 반납 예정 칸 추가 (맨 끝에 붙이기)
create or replace view public.car_status with (security_invoker = true) as
select c.*,
       case when t.id is not null then '사용 중'
            when c.in_repair     then '정비중'
            else '대기' end as status,
       t.id as trip_id, t.user_name, t.dept, t.dest, t.out_at,
       t.due_at
from public.cars c
left join public.trips t on t.plate = c.plate and t.ret_at is null;
