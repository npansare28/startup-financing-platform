USE startup_financing_platform;

CREATE TABLE pitcher_profiles (
    pitcher_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    startup_name    VARCHAR(150),
    industry        VARCHAR(100),
    description     TEXT,
    stage           VARCHAR(50),
    funding_required DECIMAL(15,2),
    location        VARCHAR(150),
    website         VARCHAR(255),
    founded_year    YEAR,
    team_size       INT,
    revenue         DECIMAL(15,2),
    traction        TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);