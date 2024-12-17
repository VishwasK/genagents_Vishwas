
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    age INTEGER,
    sex VARCHAR(20),
    ethnicity VARCHAR(100),
    race VARCHAR(100),
    political_views VARCHAR(100),
    education VARCHAR(100),
    occupation VARCHAR(100),
    religion VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(2),
    data JSONB -- Store full agent data
);

CREATE INDEX idx_agents_age ON agents(age);
CREATE INDEX idx_agents_sex ON agents(sex);
CREATE INDEX idx_agents_ethnicity ON agents(ethnicity); 
CREATE INDEX idx_agents_race ON agents(race);
CREATE INDEX idx_agents_political_views ON agents(political_views);
CREATE INDEX idx_agents_education ON agents(education);
CREATE INDEX idx_agents_religion ON agents(religion);
CREATE INDEX idx_agents_location ON agents(city, state);
