do $$
declare
  existing_job_id bigint;
begin
  if to_regclass('cron.job') is not null then
    execute
      'select jobid from cron.job where jobname = $1 limit 1'
      into existing_job_id
      using 'daily-event-posters';
    if existing_job_id is not null then
      execute 'select cron.unschedule($1)' using existing_job_id;
    end if;
  end if;
end;
$$;

drop function if exists public.configure_poster_cron(text, text, text);
