-- Extend user_watchlist with notification preferences
alter table if exists user_watchlist
  add column if not exists notify_via_email boolean not null default true,
  add column if not exists user_email text,
  add column if not exists last_notified_at timestamptz,
  add column if not exists last_change_digest text;

-- Backfill stored email addresses from auth.users when possible
update user_watchlist uw
set user_email = auth_user.email
from auth.users as auth_user
where uw.user_email is null
  and auth_user.id = uw.user_id;
