CREATE TABLE IF NOT EXISTS replyToClaimType (
    claimReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    claimReplyType TEXT NOT NULL
);

INSERT INTO replyToClaimType (claimReplyType) VALUES ('Clarification');
INSERT INTO replyToClaimType (claimReplyType) VALUES ('Supporting Argument');
INSERT INTO replyToClaimType (claimReplyType) VALUES ('Counterargument');