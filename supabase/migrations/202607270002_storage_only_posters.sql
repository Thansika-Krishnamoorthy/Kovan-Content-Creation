-- Forward migration for projects that applied the earlier email-capable schema.
-- It is intentionally safe after a fresh storage-only installation as well.

drop view if exists public.delivery_context;

alter table public.deliveries
  drop constraint if exists deliveries_channel_check;

alter table public.deliveries
  alter column status drop default,
  alter column status type text using status::text;

update public.deliveries
set
  channel = 'storage',
  status = case
    when status in ('generated', 'sent') then 'stored'
    else status
  end;

drop type public.poster_delivery_status;
create type public.poster_delivery_status as enum (
  'pending',
  'processing',
  'stored',
  'failed'
);

alter table public.deliveries
  alter column status type public.poster_delivery_status
    using status::public.poster_delivery_status,
  alter column status set default 'pending';

alter table public.deliveries
  add constraint deliveries_channel_check check (channel in ('storage'));

alter table public.people drop column if exists email;
alter table public.deliveries drop column if exists sent_at;

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

create or replace view public.delivery_context
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

revoke all on public.delivery_context from anon, authenticated;
revoke execute on function public.claim_poster_delivery(uuid)
from public, anon, authenticated;
grant execute on function public.claim_poster_delivery(uuid) to service_role;
