alter table public.poster_runs
  add column if not exists teams_delivered_at timestamptz,
  add column if not exists teams_error text;

create index if not exists poster_runs_teams_pending_idx
on public.poster_runs(occurrence_date)
where status = 'stored' and teams_delivered_at is null;
