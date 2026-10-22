USE startup_financing_platform;

CREATE TABLE profile_views (
    view_id     INT AUTO_INCREMENT PRIMARY KEY,
    viewer_id   INT NOT NULL,
    viewed_id   INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (viewer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (viewed_id) REFERENCES users(user_id) ON DELETE CASCADE
);