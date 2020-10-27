DROP DATABASE IF EXISTS trump;
CREATE DATABASE IF NOT EXISTS trump;
use trump;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id int NOT NULL AUTO_INCREMENT key,
    name varchar(256) NOT NULL UNIQUE,
    oldPass varchar(256) NOT NULL,
    newPass varchar(256) DEFAULT NULL,
    image varchar(256) NOT NULL DEFAULT "https://i.imgur.com/C35yeEC.jpg"
);
DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
    id int NOT NULL AUTO_INCREMENT key,
    page varchar(256) NOT NULL,
    text varchar(256) NOT NULL,
    userId int NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(id)
);
