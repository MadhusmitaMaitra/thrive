-- Table for user accounts
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

-- Table for user's tasks
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'todo', -- 'todo' or 'done'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date TEXT, -- <-- Added: stores the day (YYYY-MM-DD) when the task was created
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Table for user's mood entries
CREATE TABLE moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood TEXT NOT NULL, -- e.g., 'happy', 'anxious', 'tired'
    note TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
