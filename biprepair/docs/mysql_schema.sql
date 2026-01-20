CREATE DATABASE IF NOT EXISTS biprepair CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biprepair;

CREATE TABLE admins (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME(6) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE appointments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    appointment_id VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    contact_number VARCHAR(30) NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    brand_model VARCHAR(150) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    issue_description LONGTEXT NOT NULL,
    preferred_datetime DATETIME(6) NOT NULL,
    location VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    admin_notes LONGTEXT,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    CONSTRAINT chk_device_type CHECK (device_type IN ('android','iphone','laptop')),
    CONSTRAINT chk_status CHECK (status IN ('pending','approved','in_progress','completed','declined'))
) ENGINE=InnoDB;
