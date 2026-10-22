USE startup_financing_platform;

CREATE TABLE swipes (
    swipe_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    target_user_id  INT NOT NULL,
    action          ENUM('RIGHT', 'LEFT') NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (target_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (user_id, target_user_id)
);