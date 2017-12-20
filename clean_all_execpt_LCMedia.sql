delete from widgets where visualization_id in (select id from visualizations where query_id in (select id from queries  where query not like '%LCM%'));
delete from visualizations where query_id in (select id from queries  where query not like '%LCM%');
delete from queries  where query not like '%LCM%';

delete from dashboards where id in (select id from dashboards where name not like '%LCM%');
