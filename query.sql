CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    hash TEXT NOT NULL,
)

CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    amount REAL NOT NULL,
    category TEXT,
    description TEXT
    FOREIGN KEY (user_id) REFERENCES users(id)
)

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    category TEXT,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)

CREATE TABLE IF NOT EXISTS budget (
    id INTEGER PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL, 
    total INTEGER, 
    category TEXT, 
    allocated_amount INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
)

CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username)