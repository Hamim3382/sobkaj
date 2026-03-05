-- ============================================================
-- Sobkaj — Migration: Add 'admin' role to users table
-- ============================================================
-- Run this in phpMyAdmin → SQL tab BEFORE using /admin_dashboard.
-- It modifies the users.role ENUM to include 'admin', then
-- creates a default admin account (change the password hash!).
-- ============================================================

USE sobkaj;

-- 1. Extend the ENUM to include 'admin'
ALTER TABLE users
    MODIFY COLUMN role ENUM('customer', 'worker', 'admin') NOT NULL;

-- 2. Insert a default admin user.
--    Password below is the bcrypt hash of: Admin@1234
--    Change this password immediately after first login.
INSERT INTO users (full_name, email, password_hash, role, phone)
VALUES (
    'Platform Admin',
    'admin@sobkaj.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'admin',
    NULL
);
