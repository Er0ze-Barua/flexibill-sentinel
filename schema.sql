CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    account_tier VARCHAR(100) DEFAULT 'Standard'  
);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE ,
    status VARCHAR(20) DEFAULT 'Active' ,
    failed_attempts_count INT DEFAULT 0,
    next_billing_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS billing_history (
    invoice_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    amount NUMERIC(10,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name,email,account_tier)
VALUES ('Eroze','eroze@test.com', 'VIP');

INSERT INTO subscriptions (user_id, status , failed_attempts_count, next_billing_date)
VALUES (1, 'Past_Due',2,'2026-06-15');

INSERT INTO billing_history (user_id, amount, payment_status)
VALUES (1,49.99,'Failed');

INSERT INTO users (name,email,account_tier)
VALUES ('Jhon Doe', 'john@test.com' , 'Standard');

INSERT INTO subscriptions (user_id,status,failed_attempts_count,next_billing_date)
VALUES (2,'Active',0,'2026-07-01');

INSERT INTO billing_history (user_id, amount , payment_status)
VALUES(2,19.99,'Disputed');