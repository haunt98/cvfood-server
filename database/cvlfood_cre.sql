revoke connect on database cvlfood from public;

select pg_terminate_backend(pg_stat_activity.pid)
from pg_stat_activity
where pg_stat_activity.datname = 'cvlfood';

drop database if exists cvlfood;
create database cvlfood owner = postgres;