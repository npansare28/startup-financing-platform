USE startup_financing_platform;

CREATE TABLE investor_profiles (
    investor_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    investor_name   VARCHAR(150),
    investor_type   VARCHAR(100),
    description     TEXT,
    location        VARCHAR(150),
    min_investment  DECIMAL(15,2),
    max_investment  DECIMAL(15,2),
    website         VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);