drop table if exists wait_times cascade;
drop table if exists web_pages cascade;
drop table if exists hospital_urls cascade;
CREATE TABLE hospital_urls (
    id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(255) NOT NULL,
    hospital_url TEXT NOT NULL,
    last_fetched TIMESTAMP,
    status VARCHAR(50)
);

CREATE TABLE wait_times (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL,
    wait_time INTEGER NOT NULL,
    fetched_at TIMESTAMP NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospital_urls (id)
);

CREATE TABLE web_pages (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL,
    page_url TEXT NOT NULL,
    content TEXT,
    relevance_score FLOAT,
    fetched_at TIMESTAMP NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospital_urls (id)
);



INSERT INTO hospital_urls (id, hospital_name, hospital_url) VALUES
    (1, 'Edward Health Elmhurst','https://www.eehealth.org');