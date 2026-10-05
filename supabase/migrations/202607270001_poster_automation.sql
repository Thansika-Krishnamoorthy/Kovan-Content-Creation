create extension if not exists pgcrypto;

create type public.poster_event_type as enum ('birthday', 'work_anniversary');
create type public.poster_delivery_status as enum (
  'pending',
  'processing',
  'stored',
  'failed'
);

create table public.people (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  photo_path text not null,
  timezone text not null default 'Asia/Kolkata',
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table public.events (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  event_type public.poster_event_type not null,
  event_date date not null,
  template_key text not null default 'birthday-default',
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table public.deliveries (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  occurrence_date date not null,
  channel text not null check (channel in ('storage')),
  poster_path text,
  status public.poster_delivery_status not null default 'pending',
  attempts integer not null default 0 check (attempts >= 0),
  error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (event_id, occurrence_date, channel)
);

create index events_person_id_idx on public.events(person_id);
create index deliveries_status_idx on public.deliveries(status, attempts);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger deliveries_set_updated_at
before update on public.deliveries
for each row execute function public.set_updated_at();

create or replace function public.events_due_on(requested_date date)
returns setof public.events
language sql
stable
security definer
set search_path = public
as $$
  select event.*
  from public.events as event
  join public.people as person on person.id = event.person_id
  where event.active
    and person.active
    and event.event_type in ('birthday', 'work_anniversary')
    and extract(month from event.event_date) = extract(month from requested_date)
    and extract(day from event.event_date) = extract(day from requested_date);
$$;

create or replace function public.claim_poster_delivery(
  requested_delivery_id uuid
)
returns setof public.deliveries
language sql
security definer
set search_path = public
as $$
  update public.deliveries
  set
    status = 'processing',
    attempts = attempts + 1,
    error = null
  where id = requested_delivery_id
    and status in ('pending', 'failed')
    and attempts < 3
  returning *;
$$;

create or replace function public.recover_stale_poster_deliveries()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  recovered integer;
begin
  update public.deliveries
  set
    status = 'failed',
    error = 'Worker claim expired before completion'
  where status = 'processing'
    and updated_at < now() - interval '15 minutes'
    and attempts < 3;
  get diagnostics recovered = row_count;
  return recovered;
end;
$$;

create view public.delivery_context
with (security_invoker = true)
as
select
  delivery.*,
  event.person_id,
  event.event_type,
  event.event_date,
  event.template_key,
  person.name as person_name,
  person.photo_path,
  person.timezone
from public.deliveries as delivery
join public.events as event on event.id = delivery.event_id
join public.people as person on person.id = event.person_id;

alter table public.people enable row level security;
alter table public.events enable row level security;
alter table public.deliveries enable row level security;

revoke all on public.people from anon, authenticated;
revoke all on public.events from anon, authenticated;
revoke all on public.deliveries from anon, authenticated;
revoke all on public.delivery_context from anon, authenticated;
revoke execute on function public.events_due_on(date) from public, anon, authenticated;
revoke execute on function public.claim_poster_delivery(uuid) from public, anon, authenticated;
revoke execute on function public.recover_stale_poster_deliveries() from public, anon, authenticated;
grant execute on function public.events_due_on(date) to service_role;
grant execute on function public.claim_poster_delivery(uuid) to service_role;
grant execute on function public.recover_stale_poster_deliveries() to service_role;

insert into storage.buckets (id, name, public)
values
  ('employee-photos', 'employee-photos', false),
  ('generated-posters', 'generated-posters', false)
on conflict (id) do update set public = false;
