CREATE TABLE orgs (
	org_id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
	org_name VARCHAR (255),
	date_created TIMESTAMP NOT NULL ,
	users_ids TEXT[]
);


CREATE TABLE users (
 	user_id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
 	fname VARCHAR (255) NOT NULL,
 	lname VARCHAR (255) NOT NULL,
 	phone VARCHAR (255) NOT NULL,
 	email VARCHAR (255) NOT NULL,
 	username VARCHAR (255) NOT NULL,
 	password TEXT NOT NULL,
	org_ids TEXT[],
	date_created TIMESTAMP NOT NULL
);

CREATE TABLE chores (
 	chore_id INTEGER PRIMARY KEY,
 	chore VARCHAR (255) NOT NULL,
	schedule_daily BOOLEAN NOT NULL,
	schedule_weekly BOOLEAN NOT NULL,
	user_id VARCHAR (255),
	org_id UUID NOT NULL,
	CONSTRAINT org_fk
		FOREIGN KEY(org_id)
			REFERENCES orgs(org_id)
			
);
