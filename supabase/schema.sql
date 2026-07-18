create extension if not exists "pgcrypto";

create table if not exists public.households (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  invite_code text not null unique default upper(substr(encode(gen_random_bytes(6), 'hex'), 1, 8)),
  created_at timestamptz not null default now()
);

create table if not exists public.household_members (
  household_id uuid not null references public.households(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'member' check (role in ('owner','member')),
  created_at timestamptz not null default now(),
  primary key (household_id, user_id),
  unique(user_id)
);

create table if not exists public.athletes (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references public.households(id) on delete cascade,
  user_id uuid references auth.users(id) on delete set null unique,
  display_name text not null,
  birth_year integer,
  height_cm numeric(5,2),
  current_weight_kg numeric(5,2),
  injury_notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.races (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references public.households(id) on delete cascade,
  name text not null,
  race_date date not null,
  race_type text not null default 'HYROX',
  category text,
  target_seconds integer,
  status text not null default 'planned'
    check (status in ('planned','active','completed','cancelled')),
  result_seconds integer,
  notes text,
  created_at timestamptz not null default now()
);

create unique index if not exists one_active_race_per_household
on public.races(household_id) where status = 'active';

create table if not exists public.activities (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  source text not null default 'manual',
  external_id text,
  activity_date timestamptz not null,
  activity_type text not null,
  title text,
  duration_seconds integer not null default 0,
  distance_meters numeric(10,2) not null default 0,
  average_hr integer,
  calories integer,
  rpe integer check (rpe between 1 and 10),
  pain_score integer check (pain_score between 0 and 10),
  pain_location text,
  trained_together boolean not null default false,
  notes text,
  raw_payload jsonb,
  created_at timestamptz not null default now()
);

create unique index if not exists unique_external_activity
on public.activities(source, external_id)
where external_id is not null;

create table if not exists public.coach_briefs (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references public.households(id) on delete cascade,
  race_id uuid references public.races(id) on delete set null,
  period_start date not null,
  period_end date not null,
  scope text not null check (scope in ('team','athlete')),
  athlete_id uuid references public.athletes(id) on delete cascade,
  headline text not null,
  summary text not null,
  focus jsonb not null default '[]'::jsonb,
  watch_list jsonb not null default '[]'::jsonb,
  model_name text,
  created_at timestamptz not null default now()
);

alter table public.households enable row level security;
alter table public.household_members enable row level security;
alter table public.athletes enable row level security;
alter table public.races enable row level security;
alter table public.activities enable row level security;
alter table public.coach_briefs enable row level security;

create or replace function public.is_household_member(target_household uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.household_members
    where household_id = target_household and user_id = auth.uid()
  );
$$;

create policy "members view households" on public.households
for select using (public.is_household_member(id));

create policy "members view membership" on public.household_members
for select using (public.is_household_member(household_id));

create policy "members view athletes" on public.athletes
for select using (public.is_household_member(household_id));

create policy "members manage athletes" on public.athletes
for all using (public.is_household_member(household_id))
with check (public.is_household_member(household_id));

create policy "members view races" on public.races
for select using (public.is_household_member(household_id));

create policy "members manage races" on public.races
for all using (public.is_household_member(household_id))
with check (public.is_household_member(household_id));

create policy "members view activities" on public.activities
for select using (
  exists (
    select 1 from public.athletes a
    where a.id = athlete_id and public.is_household_member(a.household_id)
  )
);

create policy "members manage activities" on public.activities
for all using (
  exists (
    select 1 from public.athletes a
    where a.id = athlete_id and public.is_household_member(a.household_id)
  )
)
with check (
  exists (
    select 1 from public.athletes a
    where a.id = athlete_id and public.is_household_member(a.household_id)
  )
);

create policy "members view briefs" on public.coach_briefs
for select using (public.is_household_member(household_id));

create policy "members manage briefs" on public.coach_briefs
for all using (public.is_household_member(household_id))
with check (public.is_household_member(household_id));

create or replace function public.bootstrap_household(
  household_name text,
  athlete_name text
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  new_household_id uuid;
begin
  if auth.uid() is null then
    raise exception 'Authentication required';
  end if;

  if exists (select 1 from household_members where user_id = auth.uid()) then
    raise exception 'This user already belongs to a household';
  end if;

  insert into households(name)
  values (trim(household_name))
  returning id into new_household_id;

  insert into household_members(household_id, user_id, role)
  values (new_household_id, auth.uid(), 'owner');

  insert into athletes(household_id, user_id, display_name)
  values (new_household_id, auth.uid(), trim(athlete_name));

  return new_household_id;
end;
$$;

create or replace function public.join_household_by_code(
  provided_invite_code text,
  athlete_name text
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  target_household_id uuid;
begin
  if auth.uid() is null then
    raise exception 'Authentication required';
  end if;

  if exists (select 1 from household_members where user_id = auth.uid()) then
    raise exception 'This user already belongs to a household';
  end if;

  select id into target_household_id
  from households
  where invite_code = upper(trim(provided_invite_code));

  if target_household_id is null then
    raise exception 'Invalid invite code';
  end if;

  insert into household_members(household_id, user_id, role)
  values (target_household_id, auth.uid(), 'member');

  insert into athletes(household_id, user_id, display_name)
  values (target_household_id, auth.uid(), trim(athlete_name));

  return target_household_id;
end;
$$;

revoke all on function public.bootstrap_household(text, text) from public;
revoke all on function public.join_household_by_code(text, text) from public;
grant execute on function public.bootstrap_household(text, text) to authenticated;
grant execute on function public.join_household_by_code(text, text) to authenticated;
