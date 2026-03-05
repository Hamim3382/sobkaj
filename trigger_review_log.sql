-- ============================================================
-- Sobkaj — AFTER INSERT Trigger on ratings
-- ============================================================
-- This trigger fires after a new review is inserted.
-- It logs the event into a `review_log` audit table.
--
-- 🚨 RUN THIS IN phpMyAdmin → SQL tab (after init_db.sql)
-- ============================================================

USE sobkaj;

-- 1. Create the audit log table
CREATE TABLE IF NOT EXISTS review_log (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    rating_id   INT NOT NULL,
    booking_id  INT NOT NULL,
    worker_id   INT NOT NULL,
    stars       INT NOT NULL,
    logged_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- 2. Create the AFTER INSERT trigger
DELIMITER $$

CREATE TRIGGER trg_after_review_insert
AFTER INSERT ON ratings
FOR EACH ROW
BEGIN
    -- Log every new review into the audit table
    INSERT INTO review_log (rating_id, booking_id, worker_id, stars)
    VALUES (NEW.rating_id, NEW.booking_id, NEW.worker_id, NEW.stars);
END$$

DELIMITER ;
