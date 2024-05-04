CREATE TABLE IF NOT EXISTS claimToClaimType (
    claimRelTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    claimRelType TEXT NOT NULL
);
INSERT INTO claimToClaimType (claimRelTypeID, claimRelType) VALUES (1, 'Opposed');
INSERT INTO claimToClaimType (claimRelTypeID, claimRelType) VALUES (2, 'Equivalent');