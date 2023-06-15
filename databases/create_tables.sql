CREATE TABLE on_premise_server (
    id SERIAL PRIMARY KEY,
    server_name VARCHAR(255),
    ip_address VARCHAR(255),
    application_name VARCHAR(255),
    environment VARCHAR(255),
    itbp_contact VARCHAR(255),
    business_contact VARCHAR(255),
    it_contact VARCHAR(255),
    os_info VARCHAR(255),
    updated_by VARCHAR(255),
    updated_time TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE vulnerabilities_statistic (
    id SERIAL PRIMARY KEY,
    server_id INT not null,
    severity_1 INT,
    severity_2 INT,
    severity_3 INT,
    severity_4 INT,
    severity_5 INT,
    updated_time TIMESTAMP DEFAULT current_timestamp,
    CONSTRAINT fk_server_id FOREIGN KEY(server_id) REFERENCES on_premise_server(id),
    CONSTRAINT uk_server_id UNIQUE(server_id)
);