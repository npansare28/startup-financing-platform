-- ============================================================
-- STARTUP FINANCING PLATFORM — MASTER DATABASE SETUP SCRIPT
-- Run this once to create and initialize the full schema
-- Usage: mysql -u root -p < setup_database.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS startup_financing_platform;
USE startup_financing_platform;

-- Drop in reverse FK order
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

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100),
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('PITCHER', 'INVESTOR') NOT NULL,
    profile_photo VARCHAR(500),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- PITCHER PROFILES
-- ============================================================
CREATE TABLE pitcher_profiles (
    pitcher_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL UNIQUE,
    startup_name     VARCHAR(150),
    industry         VARCHAR(100),
    description      TEXT,
    stage            VARCHAR(50),
    funding_required DECIMAL(15,2),
    location         VARCHAR(150),
    website          VARCHAR(255),
    founded_year     YEAR,
    team_size        INT,
    revenue          DECIMAL(15,2),
    traction         TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- INVESTOR PROFILES
-- ============================================================
CREATE TABLE investor_profiles (
    investor_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL UNIQUE,
    investor_name  VARCHAR(150),
    investor_type  VARCHAR(100),
    description    TEXT,
    location       VARCHAR(150),
    min_investment DECIMAL(15,2),
    max_investment DECIMAL(15,2),
    website        VARCHAR(255),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- INVESTOR INDUSTRIES (many-to-many)
-- ============================================================
CREATE TABLE investor_industries (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    industry    VARCHAR(100) NOT NULL,
    FOREIGN KEY (investor_id) REFERENCES investor_profiles(investor_id) ON DELETE CASCADE
);

-- ============================================================
-- INVESTOR STAGES (many-to-many)
-- ============================================================
CREATE TABLE investor_stages (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    stage       VARCHAR(50) NOT NULL,
    FOREIGN KEY (investor_id) REFERENCES investor_profiles(investor_id) ON DELETE CASCADE
);

-- ============================================================
-- SWIPES
-- ============================================================
CREATE TABLE swipes (
    swipe_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    target_user_id INT NOT NULL,
    action         ENUM('RIGHT', 'LEFT') NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (target_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (user_id, target_user_id)
);

-- ============================================================
-- POSTS
-- ============================================================
CREATE TABLE posts (
    post_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    content    TEXT NOT NULL,
    media_url  VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- POST LIKES
-- ============================================================
CREATE TABLE post_likes (
    like_id    INT AUTO_INCREMENT PRIMARY KEY,
    post_id    INT NOT NULL,
    user_id    INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (post_id, user_id)
);

-- ============================================================
-- COMMENTS
-- ============================================================
CREATE TABLE comments (
    comment_id   INT AUTO_INCREMENT PRIMARY KEY,
    post_id      INT NOT NULL,
    user_id      INT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- CONNECTIONS
-- ============================================================
CREATE TABLE connections (
    connection_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id     INT NOT NULL,
    receiver_id   INT NOT NULL,
    status        ENUM('PENDING', 'ACCEPTED', 'REJECTED') DEFAULT 'ACCEPTED',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (sender_id, receiver_id)
);

-- ============================================================
-- PROFILE VIEWS
-- ============================================================
CREATE TABLE profile_views (
    view_id    INT AUTO_INCREMENT PRIMARY KEY,
    viewer_id  INT NOT NULL,
    viewed_id  INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (viewer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (viewed_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    type            VARCHAR(50) NOT NULL,
    message         VARCHAR(255) NOT NULL,
    reference_id    INT,
    sender_id       INT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ============================================================
-- SEARCH HISTORY
-- ============================================================
CREATE TABLE search_history (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    query      VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

SELECT 'Database setup complete!' AS status;
