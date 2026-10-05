-- Store birthdays as month/day values instead of an artificial reference year.

alter table public.people
  add column if not exists employee_id text;

drop index if exists public.people_employee_id_uidx;
create unique index people_employee_id_uidx
  on public.people (employee_id);

alter table public.events
  alter column event_date drop not null;

alter table public.events
  add column if not exists event_month smallint,
  add column if not exists event_day smallint;

-- Preserve existing birthday month/day values before removing their artificial
-- date year. Existing anniversary dates remain unchanged.
update public.events
set
  event_month = extract(month from event_date)::smallint,
  event_day = extract(day from event_date)::smallint,
  event_date = null
where event_type = 'birthday';

update public.events
set event_month = null, event_day = null
where event_type = 'work_anniversary';

alter table public.events
  add constraint events_date_model_check check (
    (event_type = 'birthday'
      and event_date is null
      and event_month is not null
      and event_day is not null)
    or
    (event_type = 'work_anniversary'
      and event_date is not null
      and event_month is null
      and event_day is null)
  ),
  add constraint events_month_day_check check (
    (event_month is null and event_day is null)
    or (
      event_month between 1 and 12
      and event_day between 1 and 31
      and (event_month not in (2, 4, 6, 9, 11)
        or event_day <= case
          when event_month = 2 then 29
          when event_month in (4, 6, 9, 11) then 30
          else 31
        end)
    )
  );

alter table public.events
  add constraint events_person_event_type_uidx unique (person_id, event_type);

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
    and (
      (event.event_type = 'birthday'
        and event.event_month = extract(month from requested_date)::smallint
        and event.event_day = extract(day from requested_date)::smallint)
      or
      (event.event_type = 'work_anniversary'
        and extract(month from event.event_date) = extract(month from requested_date)
        and extract(day from event.event_date) = extract(day from requested_date))
    );
$$;

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
    and (
      (event.event_type = 'birthday'
        and event.event_month = extract(month from requested_date)::smallint
        and event.event_day = extract(day from requested_date)::smallint)
      or
      (event.event_type = 'work_anniversary'
        and extract(month from event.event_date) = extract(month from requested_date)
        and extract(day from event.event_date) = extract(day from requested_date))
    );
$$;
