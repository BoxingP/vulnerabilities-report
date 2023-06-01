CREATE TABLE on_premise_server (
    id SERIAL PRIMARY KEY,
    server_name VARCHAR(255),
    application_name VARCHAR(255),
    os_info VARCHAR(255),
    it_contact VARCHAR(255),
    updated_time TIMESTAMP DEFAULT current_timestamp
);