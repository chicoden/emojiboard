CREATE DATABASE emo_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE emo_db;

CREATE TABLE guilds (
    guild_id BIGINT UNSIGNED,
    is_tracked BIT,
    PRIMARY KEY (guild_id)
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

-- INSERT INTO guilds VALUES (1306709274713391235, 1);
-- INSERT INTO guilds VALUES (123456789, 0);
-- INSERT INTO emoji (is_default, is_animated, emoji_id, emoji_name) VALUES (1, 0,                   0, "⭐"        );
-- INSERT INTO emoji (is_default, is_animated, emoji_id, emoji_name) VALUES (0, 0, 1311363042415611964, "kekw"     );
-- INSERT INTO emoji (is_default, is_animated, emoji_id, emoji_name) VALUES (1, 0,                   0, "🕺"        );
-- INSERT INTO emoji (is_default, is_animated, emoji_id, emoji_name) VALUES (0, 1, 1452957163592093756, "happyfrog");
-- INSERT INTO tracked_emoji VALUES (1306709274713391235, 1,  1);
-- INSERT INTO tracked_emoji VALUES (1306709274713391235, 2, 10);
-- INSERT INTO tracked_emoji VALUES (1306709274713391235, 4, 12);

SELECT table_name FROM information_schema.tables WHERE table_schema = "emo_db";
