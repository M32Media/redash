CREATE TABLE visualization_referrer(
    visualization_id integer REFERENCES visualizations (id),
    referrer Text ,
    PRIMARY KEY (visualization_id, referrer)
);
#Need to be psql (or superuser) to run
GRANT ALL ON visualization_referrer to redash;
GRANT ALL ON visualization_referrer to dev;