PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Songs" (
	"Title"	TEXT NOT NULL,
	"URL"	TEXT NOT NULL,
	"Status"	TEXT NOT NULL DEFAULT 'Queued',
	"Priority"	INTEGER NOT NULL DEFAULT 0 COLLATE BINARY,
	"TwitchIDRequester"	INTEGER NOT NULL,
	FOREIGN KEY("TwitchIDRequester") REFERENCES "Users"("TwitchID")
);
INSERT INTO Songs VALUES('Happy by Fjun','https://soundcloud.com/fjun/happy','Queued',0,709104352);
INSERT INTO Songs VALUES('hello world by Louie Zong','https://soundcloud.com/louie-zong/hello-world','Queued',1,709104352);
CREATE TABLE IF NOT EXISTS "Users" (
	"TwitchID"	INTEGER NOT NULL UNIQUE,
	"Username"	TEXT NOT NULL,
	PRIMARY KEY("TwitchID")
);
INSERT INTO Users VALUES(709104352,'orendcross');
DELETE FROM sqlite_sequence;
COMMIT;
