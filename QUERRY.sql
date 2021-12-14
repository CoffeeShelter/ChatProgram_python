CREATE DATABASE IF NOT EXISTS CHATTING;

USE CHATTING;

CREATE TABLE IF NOT EXISTS USER_
(
	ID VARCHAR(200) NOT NULL,
    PWD VARCHAR(200) NOT NULL,
    NAME_ VARCHAR(300) NOT NULL,
    EMAIL VARCHAR(20) NOT NULL,
    DATE_ DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(ID)
);

INSERT INTO USER_(ID, PWD, NAME_, EMAIL) VALUES("root", "1234", "운영자", "test@gmail.com");
INSERT INTO USER_(ID, PWD, NAME_, EMAIL) VALUES("test1", "1234", "test1", "test1@gmail.com");

SELECT * FROM USER_;

SELECT * FROM USER_ WHERE ID="root";