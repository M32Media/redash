CREATE TABLE users_queries(
	user_id integer REFERENCES users (id),
	query_id integer REFERENCES queries (id),
	PRIMARY KEY (user_id, query_id)
);
