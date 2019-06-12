DROP TABLE dashgroups CASCADE;
DROP TABLE users_dashgroups CASCADE;
DROP TABLE dashgroups_dashboards CASCADE;

CREATE TABLE dashgroups(
	id SERIAL PRIMARY KEY,
	name varchar(50)
);


CREATE TABLE users_dashgroups(
	user_id integer REFERENCES users (id),
	dashgroup_id integer REFERENCES dashgroups (id) ON DELETE CASCADE,
	PRIMARY KEY (user_id, dashgroup_id)
);

CREATE TABLE dashgroups_dashboards(
	dashgroup_id integer REFERENCES dashgroups (id) ON DELETE CASCADE,
	dashboard_id integer REFERENCES dashboards (id) ON DELETE CASCADE,
	PRIMARY KEY(dashgroup_id, dashboard_id)
);

insert into dashgroups (name) values ('TestGroup');
insert into users_dashgroups (user_id, dashgroup_id) values (1,1);
insert into dashgroups_dashboards (dashgroup_id, dashboard_id) values (1,3);
