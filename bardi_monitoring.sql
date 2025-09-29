-- bardi_monitoring.sql
SET FOREIGN_KEY_CHECKS=0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

-- Table structure for table device_info
CREATE TABLE device_info (
  id int(11) NOT NULL,
  device_id varchar(255) NOT NULL,
  product_name varchar(255) DEFAULT NULL,
  ip_address varchar(100) DEFAULT NULL,
  online_status varchar(50) DEFAULT NULL,
  last_updated datetime DEFAULT (datetime('now'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for table device_logs
CREATE TABLE device_logs (
  id int(11) NOT NULL,
  device_id varchar(255) NOT NULL,
  switch_name varchar(100) NOT NULL,
  status varchar(50) NOT NULL,
  created_at datetime DEFAULT (datetime('now'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for table device_info
ALTER TABLE device_info
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY device_id (device_id),
  ADD KEY idx_last_updated (last_updated);

-- Indexes for table device_logs
ALTER TABLE device_logs
  ADD PRIMARY KEY (id),
  ADD KEY idx_device_id (device_id),
  ADD KEY idx_switch_name (switch_name),
  ADD KEY idx_created_at (created_at),
  ADD KEY idx_switch_created (switch_name,created_at);

-- AUTO_INCREMENT for table device_info
ALTER TABLE device_info
  MODIFY id int(11) NOT NULL AUTO_INCREMENT;

-- AUTO_INCREMENT for table device_logs
ALTER TABLE device_logs
  MODIFY id int(11) NOT NULL AUTO_INCREMENT;
SET FOREIGN_KEY_CHECKS=1;
COMMIT;