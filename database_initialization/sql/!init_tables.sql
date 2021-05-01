/*
	Models version: 1.0
	Generation time: 2021-04-30T11:38:35.437853
*/

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `login` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `about_me` TEXT DEFAULT NULL,
    `image_path` VARCHAR(255) DEFAULT NULL,
    `is_admin` TINYINT(1) NOT NULL DEFAULT '0',
    `is_moderator` TINYINT(1) NOT NULL DEFAULT '0',
    PRIMARY KEY (`id`)
)  ENGINE=INNODB;
    

CREATE VIEW `moderators` AS 
    SELECT * FROM `users` WHERE `is_moderator` = TRUE;
    

CREATE TABLE IF NOT EXISTS `post_rubrics` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `user_id` INT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE SET NULL ON UPDATE NO ACTION
)  ENGINE=INNODB;
    

CREATE TABLE IF NOT EXISTS `posts` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `user_id` INT NULL,
    `rubric_id` INT NULL,
    PRIMARY KEY (`id`),
    FULLTEXT ( `title` , `content` ),
    FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE SET NULL ON UPDATE NO ACTION,
    FOREIGN KEY (`rubric_id`)
        REFERENCES `post_rubrics` (`id`)
        ON DELETE SET NULL ON UPDATE NO ACTION
)  ENGINE=INNODB;
    

CREATE TABLE IF NOT EXISTS `note_rubrics` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE ON UPDATE NO ACTION
)  ENGINE=INNODB;
    

CREATE TABLE IF NOT EXISTS `notes` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `content` TEXT NOT NULL,
    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `rubric_id` INT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    FULLTEXT ( `content` ),
    FOREIGN KEY (`rubric_id`)
        REFERENCES `note_rubrics` (`id`)
        ON DELETE CASCADE ON UPDATE NO ACTION,
    FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE ON UPDATE NO ACTION
)  ENGINE=INNODB;
    