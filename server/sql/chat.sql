CREATE TABLE ChatMessages (
    idx INTEGER NOT NULL AUTOINCREMENT PRIMARY KEY,
    sender varchar(255) NOT NULL,
    time INTEGER NOT NULL,
    content TEXT,
    media TEXT,
    type TEXT
);