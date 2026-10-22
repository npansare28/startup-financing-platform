CREATE DATABASE IF NOT EXISTS startup_financing_platform;
USE startup_financing_platform;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('INVESTOR', 'PITCHER') NOT NULL,
    profile_photo VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE pitcher_profiles (
    pitcher_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    startup_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    description TEXT,
    stage VARCHAR(50),
    funding_required DECIMAL(15,2),
    location VARCHAR(150),
    website VARCHAR(255),
    founded_year YEAR,
    team_size INT,
    revenue DECIMAL(15,2),
    traction TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE investor_profiles (
    investor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    investor_name VARCHAR(150),
    investor_type VARCHAR(100),
    description TEXT,
    location VARCHAR(150),
    min_investment DECIMAL(15,2),
    max_investment DECIMAL(15,2),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE investor_industries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    industry VARCHAR(100) NOT NULL,

    FOREIGN KEY (investor_id) REFERENCES investor_profiles(investor_id)
);
CREATE TABLE investor_stages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investor_id INT NOT NULL,
    stage VARCHAR(50) NOT NULL,

    FOREIGN KEY (investor_id) REFERENCES investor_profiles(investor_id)
);
CREATE TABLE swipes (
    swipe_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_user_id INT NOT NULL,
    action ENUM('RIGHT', 'LEFT') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (target_user_id) REFERENCES users(user_id),

    UNIQUE (user_id, target_user_id)
);
CREATE TABLE posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    media_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE post_likes (
    like_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),

    UNIQUE (post_id, user_id)
);
CREATE TABLE comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE connections (
    connection_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    status ENUM('PENDING', 'ACCEPTED', 'REJECTED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id),

    UNIQUE (sender_id, receiver_id)
);
CREATE TABLE profile_views (
    view_id INT AUTO_INCREMENT PRIMARY KEY,
    viewer_id INT NOT NULL,
    profile_user_id INT NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (viewer_id) REFERENCES users(user_id),
    FOREIGN KEY (profile_user_id) REFERENCES users(user_id)
);