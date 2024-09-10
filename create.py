import sqlite3

con = sqlite3.connect('db.sql')
cur = con.cursor()

create_interviewee = """
CREATE TABLE IF NOT EXISTS interviewee (
    case_no INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    pseudonym VARCHAR(255) NOT NULL,
    recorded BOOLEAN NOT NULL,
    consent VARCHAR(255) NOT NULL,
    partial_consent TEXT,
    past_interviews INTEGER NOT NULL,
    past_dates TEXT NOT NULL,
    your_name VARCHAR(255) NOT NULL,
    interviewer TEXT NOT NULL,
    age_range VARCHAR(255) NOT NULL,
    gender VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    profession_type VARCHAR(255) NOT NULL,
    professional_title VARCHAR(255) NOT NULL,
    works_in_gov BOOLEAN NOT NULL,
    geographic_level TEXT,
    sector VARCHAR(255),
    works_in_org BOOLEAN NOT NULL,
    country_of_organization TEXT,
    geographic_reach TEXT,
    years_of_operation VARCHAR(255),
    formality VARCHAR(255),
    types_of_activities TEXT,
    types_of_violence TEXT,
    org_works_in_conflict BOOLEAN,
    currently_lives_in_conflict BOOLEAN,
    cur_name_of_conflict VARCHAR(255),
    gang_faction VARCHAR(255),
    previously_lives_in_conflict BOOLEAN,
    prev_name_of_conflict VARCHAR(255),
    works_in_conflict BOOLEAN NOT NULL,
    lived_experience_of_violence BOOLEAN NOT NULL,
    violence_types TEXT,
    gang_violence_type TEXT,
    random_crime_type TEXT,
    intimate_violence_type TEXT,
    state_violence_type TEXT,
    other_violence_type TEXT
);
""".strip()

create_list = [
    create_interviewee,
]

for create in create_list:
    cur.execute(create)
    con.commit()

cur.close()
con.close()
