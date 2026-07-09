USE student_assistant;

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipient_id VARCHAR(50) NOT NULL,
    recipient_type VARCHAR(20) NOT NULL COMMENT 'student / teacher',
    type VARCHAR(30) NOT NULL COMMENT 'new_application / approval_result / risk_alert',
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_read TINYINT NOT NULL DEFAULT 0 COMMENT '0=unread, 1=read',
    related_id INT COMMENT 'FK to application or alert ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_recipient_read (recipient_id, recipient_type, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sync_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sync_type VARCHAR(30) NOT NULL COMMENT 'campus_ddl / crm_progress',
    status VARCHAR(20) NOT NULL COMMENT 'running / success / failed',
    records_count INT DEFAULT 0,
    error_message TEXT,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME,
    INDEX idx_type_time (sync_type, started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS kb_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) COMMENT 'life abroad / study guide / policy',
    source_file VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FULLTEXT INDEX ft_content (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
