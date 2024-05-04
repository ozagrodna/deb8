DROP TABLE IF EXISTS topic;
CREATE TABLE topic (
    topicID INTEGER PRIMARY KEY AUTOINCREMENT,
    topicName TEXT NOT NULL,
    postingUser INTEGER,
    creationTime INTEGER NOT NULL DEFAULT (strftime('%m/%d/%Y %H:%M', 'now')),
    updateTime INTEGER NOT NULL DEFAULT (strftime('%m/%d/%Y %H:%M', 'now')),
    FOREIGN KEY (postingUser) REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE
);