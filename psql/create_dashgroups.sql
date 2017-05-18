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
