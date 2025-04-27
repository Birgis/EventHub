-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    location TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Registrations table
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (event_id) REFERENCES events (id),
    UNIQUE(user_id, event_id)
);

INSERT INTO users (name, email, password_hash) VALUES ('user', 'user@example.com', 'pbkdf2:sha256:600000$va4JlJENESsLpHYL$8657d500aad01a0f1a495a62367d3a24bdb6d27e16e484de2c457490d90647d7');
INSERT INTO users (name, email, password_hash) VALUES ('user2', 'user2@example.com', 'pbkdf2:sha256:600000$va4JlJENESsLpHYL$8657d500aad01a0f1a495a62367d3a24bdb6d27e16e484de2c457490d90647d7');

INSERT INTO events (user_id, name, description, date, location) VALUES (1, 'Første Event', 'Dette er en testevent i fremtiden', datetime('now', '+2 days'), 'Oslo');
INSERT INTO events (user_id, name, description, date, location) VALUES (2, 'Andre Event', 'Dette er en annen testevent i fremtiden', datetime('now', '+5 days'), 'Bergen');
INSERT INTO events (user_id, name, description, date, location) VALUES (1, 'Gammelt Event', 'Dette er et gammelt event', datetime('now', '-5 days'), 'Trondheim');

INSERT INTO registrations (user_id, event_id) VALUES (2, 1); 