CREATE TABLE IF NOT EXISTS replyToReplyType (
    replyReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    replyReplyType TEXT NOT NULL
);
INSERT INTO replyToReplyType (replyReplyType) VALUES ('Evidence');
INSERT INTO replyToReplyType (replyReplyType) VALUES ('Support');
INSERT INTO replyToReplyType (replyReplyType) VALUES ('Rebuttal');