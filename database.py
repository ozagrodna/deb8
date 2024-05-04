import sqlite3

def create_user_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS user;
        CREATE TABLE IF NOT EXISTS user (
            userID INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT NOT NULL UNIQUE,
            passwordHash TEXT NOT NULL,
            isAdmin BOOLEAN NOT NULL DEFAULT 0,
            creationTime INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            lastVisit INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()

def create_topic_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS topic;
        CREATE TABLE topic (
            topicID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            topicName TEXT NOT NULL,
            postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE,
            creationTime INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updateTime INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    connection.commit()
    connection.close()


def create_claim_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS claim;
        CREATE TABLE IF NOT EXISTS claim (
            claimID INTEGER PRIMARY KEY AUTOINCREMENT,
            topic INTEGER NOT NULL REFERENCES topic(topicID) ON DELETE CASCADE ON UPDATE CASCADE,
            postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE,
            creationTime INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updateTime INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            claimHeader VARCHAR(100),
            text TEXT NOT NULL
        );
    ''')
    connection.commit()
    connection.close()



def create_claim_to_claim_type_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claimToClaimType (
            claimRelTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            claimRelType TEXT NOT NULL
        )
    ''')
    cursor.executemany('''
        INSERT INTO claimToClaimType (claimRelType) VALUES (?)
    ''', [('Opposed',), ('Equivalent',)])
    connection.commit()
    connection.close()  

def create_claim_to_claim_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claimToClaim (
            claimRelID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            first INTEGER NOT NULL REFERENCES claim(claimID) ON DELETE CASCADE ON UPDATE CASCADE,
            second INTEGER NOT NULL REFERENCES claim(claimID) ON DELETE CASCADE ON UPDATE CASCADE,
            claimRelType INTEGER NOT NULL REFERENCES claimToClaimType(claimRelTypeID) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT claimToClaimUnique UNIQUE (first, second)
        )
    ''')
    connection.commit()
    connection.close()


def create_replyText_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS replyText;
        CREATE TABLE replyText (
            replyTextID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE,
            creationTime INTEGER NOT NULL,
            text TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

def create_replyToClaimType_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS replyToClaimType;
        CREATE TABLE replyToClaimType (
            claimReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            claimReplyType TEXT NOT NULL
        )
    ''')
    cursor.executemany('''
        INSERT INTO replyToClaimType (claimReplyType) VALUES (?)
    ''', [("Clarification",), ("Supporting Argument",), ("Counterargument",)])
    connection.commit()
    connection.close()

def create_replyToClaim_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS replyToClaim;
        CREATE TABLE replyToClaim (
            replyToClaimID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            reply INTEGER NOT NULL REFERENCES replyText (replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,
            claim INTEGER NOT NULL REFERENCES claim (claimID) ON DELETE CASCADE ON UPDATE CASCADE,
            replyToClaimRelType INTEGER NOT NULL REFERENCES replyToClaimType(claimReplyTypeID) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')
    connection.commit()
    connection.close()

def create_replyToReplyType_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS replyToReplyType;
        CREATE TABLE replyToReplyType (
            replyReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            replyReplyType TEXT NOT NULL
        )
    ''')
    cursor.executemany('''
        INSERT INTO replyToReplyType (replyReplyType) VALUES (?)
    ''', [("Evidence",), ("Support",), ("Rebuttal",)])
    connection.commit()
    connection.close()

def create_replyToReply_table():
    connection = sqlite3.connect('debate.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS replyToReply;
        CREATE TABLE replyToReply (
            replyToReplyID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            reply INTEGER NOT NULL REFERENCES replyText(replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,
            parent INTEGER NOT NULL REFERENCES replyText(replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,
            replyToReplyRelType INTEGER NOT NULL REFERENCES replyToReplyType(replyReplyTypeID) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')
    connection.commit()
    connection.close()