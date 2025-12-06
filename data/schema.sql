CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS history (
    round_no INT PRIMARY KEY,
    num1 INT,
    num2 INT,
    num3 INT,
    num4 INT,
    num5 INT,
    num6 INT,
    bonus INT,
    draw_date DATE,
    first_prize_auto INT DEFAULT 0,
    first_prize_manual INT DEFAULT 0,
    first_prize_semi_auto INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS my_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    round_no INT,
    num1 INT,
    num2 INT,
    num3 INT,
    num4 INT,
    num5 INT,
    num6 INT,
    rank_val VARCHAR(20),
    matched_count INT,
    bonus_matched BOOLEAN,
    memo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS winning_stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_no INT,
    store_name VARCHAR(100),
    choice_type VARCHAR(20),
    address VARCHAR(255),
    FOREIGN KEY (round_no) REFERENCES history(round_no)
);

CREATE TABLE IF NOT EXISTS prizes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_no INT,
    rank_no INT,
    total_price BIGINT,
    winner_count INT,
    win_amount BIGINT,
    FOREIGN KEY (round_no) REFERENCES history(round_no)
);
