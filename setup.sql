CREATE DATABASE emo_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE emo_db;

CREATE TABLE guilds (
    guild_id BIGINT UNSIGNED,
    is_tracked BIT
);

CREATE TABLE tracked_emoji (
    guild_id BIGINT UNSIGNED,
    emoji_index BIGINT UNSIGNED,
    emoji_weight INT
);

CREATE TABLE emoji (
    emoji_index BIGINT UNSIGNED AUTO_INCREMENT,
    is_default BIT,
    is_animated BIT,
    emoji_id BIGINT UNSIGNED,
    emoji_name VARCHAR(32),
    PRIMARY KEY (emoji_index)
);

SELECT table_name FROM information_schema.tables WHERE table_schema = "emo_db";
