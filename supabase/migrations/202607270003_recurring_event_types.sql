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

revoke execute on function public.events_due_on(date)
from public, anon, authenticated;
grant execute on function public.events_due_on(date) to service_role;
