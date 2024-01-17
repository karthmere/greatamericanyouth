CREATE TABLE Models(
    model TEXT NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES User(username)
);
