create type public.poster_run_status as enum ('processing', 'stored', 'failed');

create table public.poster_runs (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  occurrence_date date not null,
  poster_path text,
  status public.poster_run_status not null default 'processing',
  attempts integer not null default 1 check (attempts between 1 and 3),
  error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (event_id, occurrence_date)
);

create index poster_runs_status_idx
on public.poster_runs(status, occurrence_date);

create trigger poster_runs_set_updated_at
before update on public.poster_runs
for each row execute function public.set_updated_at();

create or replace function public.poster_events_due_on(requested_date date)
returns table (
  event_id uuid,
  event_type public.poster_event_type,
  event_date date,
  template_key text,
  person_id uuid,
  person_name text,
  photo_path text
)
language sql
stable
security definer
set search_path = public
as $$
  select
    event.id,
    event.event_type,
    event.event_date,
    event.template_key,
    person.id,
    person.name,
    person.photo_path
  from public.events as event
  join public.people as person on person.id = event.person_id
  where event.active
    and person.active
    and event.event_type in ('birthday', 'work_anniversary')
    and extract(month from event.event_date) = extract(month from requested_date)
    and extract(day from event.event_date) = extract(day from requested_date);
$$;

create or replace function public.claim_poster_run(
  requested_event_id uuid,
  requested_date date
)
returns setof public.poster_runs
language sql
security definer
set search_path = public
as $$
  insert into public.poster_runs (event_id, occurrence_date)
  values (requested_event_id, requested_date)
  on conflict (event_id, occurrence_date) do update
  set
    status = 'processing',
    attempts = poster_runs.attempts + 1,
    error = null
  where (
      poster_runs.status = 'failed'
      or (
        poster_runs.status = 'processing'
        and poster_runs.updated_at < now() - interval '10 minutes'
      )
    )
    and poster_runs.attempts < 3
  returning *;
$$;

alter table public.poster_runs enable row level security;
revoke all on public.poster_runs from anon, authenticated;
revoke execute on function public.poster_events_due_on(date)
from public, anon, authenticated;
revoke execute on function public.claim_poster_run(uuid, date)
from public, anon, authenticated;
grant execute on function public.poster_events_due_on(date) to service_role;
grant execute on function public.claim_poster_run(uuid, date) to service_role;

insert into storage.buckets (id, name, public)
values ('brand-assets', 'brand-assets', false)
on conflict (id) do update set public = false;

drop view if exists public.delivery_context;
drop function if exists public.claim_poster_delivery(uuid);
drop function if exists public.recover_stale_poster_deliveries();
drop function if exists public.events_due_on(date);
drop table if exists public.deliveries;
drop type if exists public.poster_delivery_status;
