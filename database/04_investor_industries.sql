USE startup_financing_platform;

CREATE TABLE investor_industries (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    industry    VARCHAR(100) NOT NULL,
    FOREIGN KEY (investor_id) REFERENCES investor_profiles(investor_id) ON DELETE CASCADE
);