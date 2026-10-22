USE startup_financing_platform;

CREATE TABLE investor_stages (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    stage       VARCHAR(50) NOT NULL,
    FOREIGN KEY (investor_id) REFERENCES investor_profiles(investor_id) ON DELETE CASCADE
);