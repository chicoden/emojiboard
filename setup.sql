CREATE DATABASE emo_db;
USE emo_db;

CREATE TABLE guilds (
    guild_id BIGINT UNSIGNED,
    is_tracked BIT
);

CREATE TABLE tracked_emoji (
    guild_id BIGINT UNSIGNED,
    emoji_index BIGINT UNSIGNED
);

CREATE TABLE emoji (
    emoji_index BIGINT UNSIGNED AUTO_INCREMENT,
    is_default BIT,
    emoji_id BIGINT UNSIGNED,
    emoji_name VARCHAR(32),
    primary key (emoji_index)
);

SELECT table_name FROM information_schema.tables WHERE table_schema = "emo_db";
