-- ============================================================
-- Sobkaj Service Marketplace — Database Initialization Script
-- ============================================================
-- Run this script in phpMyAdmin (XAMPP) to create the database,
-- all tables, and seed the skills lookup table.
-- ============================================================

CREATE DATABASE IF NOT EXISTS sobkaj;
USE sobkaj;

-- ============================================================
-- 1. USERS
-- ============================================================
CREATE TABLE users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100)  NOT NULL,
    email          VARCHAR(150)  NOT NULL UNIQUE,
    password_hash  VARCHAR(255)  NOT NULL,
    role           ENUM('customer', 'worker') NOT NULL,
    phone          VARCHAR(20),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 2. WORKER_PROFILES
-- ============================================================
CREATE TABLE worker_profiles (
    profile_id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT NOT NULL UNIQUE,
    nid_number          VARCHAR(50),
    police_verified     BOOLEAN DEFAULT FALSE,
    brac_trained        BOOLEAN DEFAULT FALSE,
    hourly_rate         DECIMAL(10, 2) DEFAULT 0.00,
    availability_status ENUM('available', 'busy', 'offline') DEFAULT 'available',
    photo_url           VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 3. SKILLS
-- ============================================================
CREATE TABLE skills (
    skill_id    INT AUTO_INCREMENT PRIMARY KEY,
    skill_name  VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB;

-- ============================================================
-- 4. WORKER_SKILLS  (junction / bridge table)
-- ============================================================
CREATE TABLE worker_skills (
    worker_id  INT NOT NULL,
    skill_id   INT NOT NULL,
    PRIMARY KEY (worker_id, skill_id),
    FOREIGN KEY (worker_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (skill_id)  REFERENCES skills(skill_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 5. BOOKINGS
-- ============================================================
CREATE TABLE bookings (
    booking_id          INT AUTO_INCREMENT PRIMARY KEY,
    customer_id         INT NOT NULL,
    worker_id           INT NOT NULL,
    service_date        DATE NOT NULL,
    hours_requested     DECIMAL(4, 2) NOT NULL,
    total_amount        DECIMAL(10, 2) DEFAULT 0.00,
    platform_commission DECIMAL(10, 2) DEFAULT 0.00,
    status              ENUM('pending', 'confirmed', 'completed', 'cancelled')
                            DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 6. RATINGS
-- ============================================================
CREATE TABLE ratings (
    rating_id   INT AUTO_INCREMENT PRIMARY KEY,
    booking_id  INT NOT NULL,
    customer_id INT NOT NULL,
    worker_id   INT NOT NULL,
    stars       INT NOT NULL CHECK (stars >= 1 AND stars <= 5),
    review_text TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id)  REFERENCES bookings(booking_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (worker_id)   REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- SEED DATA — Skills
-- ============================================================
INSERT INTO skills (skill_name, description) VALUES
    ('Plumber',      'Fixes pipes, faucets, and drainage systems'),
    ('Electrician',  'Handles wiring, electrical repairs, and installations'),
    ('Maid',         'Provides cleaning and household maintenance services'),
    ('Babysitter',   'Takes care of children in the absence of parents'),
    ('Carpenter',    'Builds and repairs wooden structures and furniture'),
    ('Painter',      'Paints walls, ceilings, and exterior surfaces'),
    ('Tutor',        'Provides academic tutoring and homework help'),
    ('Cook',         'Prepares meals and manages kitchen duties');
