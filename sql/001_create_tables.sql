CREATE TABLE IF NOT EXISTS raw_customers (
    customer_id   INTEGER,
    full_name     TEXT,
    city          TEXT,
    created_at    DATE
);

CREATE TABLE IF NOT EXISTS raw_accounts (
    account_id     INTEGER,
    customer_id    INTEGER,
    account_type   TEXT,
    currency       TEXT,
    opened_at      DATE,
    status         TEXT
);

CREATE TABLE IF NOT EXISTS raw_transactions (
    transaction_id   INTEGER,
    account_id       INTEGER,
    currency         TEXT,
    transaction_type TEXT,
    amount           NUMERIC(12, 2),
    transaction_ts   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stg_transactions (
    transaction_id   INTEGER PRIMARY KEY,
    account_id       INTEGER,
    currency         TEXT,
    transaction_type TEXT,
    amount           NUMERIC(12, 2) CHECK (amount > 0),
    transaction_ts   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rejected_transactions (
    transaction_id   INTEGER PRIMARY KEY,
    account_id       INTEGER,
    currency         TEXT,
    transaction_type TEXT,
    amount           NUMERIC(12, 2),
    transaction_ts   TIMESTAMP,
    reject_reasons   TEXT
);