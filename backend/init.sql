-- NutriLens Database Initialization
-- This file is executed when the MySQL container is first created

-- Ensure the database exists
CREATE DATABASE IF NOT EXISTS nutrilens_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON nutrilens_db.* TO 'nutrilens'@'%';
FLUSH PRIVILEGES;
