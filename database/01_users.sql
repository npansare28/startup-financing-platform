USE startup_financing_platform;

DROP TABLE IF EXISTS search_history;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS profile_views;
DROP TABLE IF EXISTS connections;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS post_likes;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS swipes;
DROP TABLE IF EXISTS investor_stages;
DROP TABLE IF EXISTS investor_industries;
DROP TABLE IF EXISTS investor_profiles;
DROP TABLE IF EXISTS pitcher_profiles;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100),
    email       VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role        ENUM('PITCHER', 'INVESTOR') NOT NULL,
    profile_photo VARCHAR(500),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);