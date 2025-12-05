-- LottoGenie Database Schema

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at VARCHAR(30)
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
    draw_date VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS my_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_no INT,
    num1 INT,
    num2 INT,
    num3 INT,
    num4 INT,
    num5 INT,
    num6 INT,
    rank_val VARCHAR(20) DEFAULT '미추첨',
    user_id INT,
    created_at VARCHAR(30),
    memo TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
