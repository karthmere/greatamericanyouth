CREATE TABLE Users(
    username varchar(255) NOT NULL,
    password varchar(500) NOT NULL,
    role varchar(255) DEFAULT 'normie',
    PRIMARY KEY (username)
);

CREATE TABLE Scores(
    username varchar(255) NOT NULL,
    score int NOT NULL,
	game varchar(255)
);

CREATE TABLE Messages(
    ID int PRIMARY KEY NOT NULL,
    content varchar(1024) NOT NULL,
    sender varchar(255) NOT NULL,
    unixtime int NOT NULL
);
