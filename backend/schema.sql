-- ============================================================
--  Frontend Framework Converter  –  Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS converter_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE converter_db;

-- Conversions table: stores every conversion job
CREATE TABLE IF NOT EXISTS conversions (
  id            INT UNSIGNED    NOT NULL AUTO_INCREMENT,
  type          ENUM('html_to_react','css_to_tailwind') NOT NULL,
  input_code    LONGTEXT        NOT NULL,
  output_code   LONGTEXT        NOT NULL,
  output_format ENUM('single','merged','zip') NOT NULL DEFAULT 'single',
  filename      VARCHAR(255)    DEFAULT NULL,
  created_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
