CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) NULL UNIQUE,
    password VARCHAR(255),
    type ENUM('ADMINISTRATOR', 'DEVICE', 'USER') DEFAULT 'USER',
    state ENUM('APPROVAL_REQUIRED','ACTIVE', 'INACTIVE', 'DELETED') DEFAULT 'APPROVAL_REQUIRED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE post_groups (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    description VARCHAR(1024) NULL,
    moderation_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE group_moderators (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    INDEX group_id (group_id),
    FOREIGN KEY (group_id)
        REFERENCES post_groups (id)
        ON DELETE CASCADE,
    user_id INT NOT NULL,
    INDEX user_id (user_id),
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

CREATE TABLE group_device_subscriptions (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    INDEX device_id (device_id),
    FOREIGN KEY (device_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    group_id INT NOT NULL,
    FOREIGN KEY (group_id)
        REFERENCES post_groups (id)
        ON DELETE CASCADE
);

CREATE TABLE posts (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NULL,
    type ENUM('IMAGE', 'HTML', 'WEB_LINK') DEFAULT 'HTML',
    start_date DATE NULL,
    end_date DATE NULL,
    image_link VARCHAR(255) NULL,
    html_content MEDIUMTEXT NULL,
    web_link VARCHAR(255) NULL,
    state ENUM('DRAFT', 'PENDING_APPROVAL', 'APPROVED','PUBLISHED', 'WITHDRAWN') DEFAULT 'DRAFT',
    created_by INT NULL,
    INDEX user_id (created_by),
    FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE post_groups_subscription (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    group_id INT NULL,
    INDEX group_id (group_id),
    FOREIGN KEY (group_id)
        REFERENCES post_groups (id)
        ON DELETE CASCADE,
    post_id INT NULL,
    INDEX post_id (post_id),
    FOREIGN KEY (post_id)
        REFERENCES posts (id)
        ON DELETE CASCADE
)