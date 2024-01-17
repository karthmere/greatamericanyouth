CREATE TABLE Articles (
    urlName varchar(255) NOT NULL PRIMARY KEY,
    title varchar(255) NOT NULL,
    author varchar(255) NOT NULL,
    date int NOT NULL,
    description TEXT,
    published int NOT NULL,
    username TEXT NOT NULL,
    thumbnail TEXT,
    avatar TEXT,
    tags TEXT,
    sections TEXT,
    FOREIGN KEY (username) REFERENCES User(username)
);