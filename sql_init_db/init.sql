-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema aiohttp_app
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `aiohttp_app` ;

-- -----------------------------------------------------
-- Schema aiohttp_app
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `aiohttp_app` DEFAULT CHARACTER SET utf8 ;
USE `aiohttp_app` ;

-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `users` ;

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `login` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `is_admin` TINYINT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `post_rubrics`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `post_rubrics` ;

CREATE TABLE IF NOT EXISTS `post_rubrics` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `user_id` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_rubrics_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_rubrics_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`id`)
    ON DELETE SET NULL
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `posts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `posts` ;

CREATE TABLE IF NOT EXISTS `posts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `content` BLOB NOT NULL,
  `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` INT NULL,
  `post_rubric_id` INT NULL,
  PRIMARY KEY (`id`),
  FULLTEXT(`title`, `content`),
  INDEX `fk_posts_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_posts_post_rubrics1_idx` (`post_rubric_id` ASC) VISIBLE,
  CONSTRAINT `fk_posts_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`id`)
    ON DELETE SET NULL
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_posts_post_rubrics1`
    FOREIGN KEY (`post_rubric_id`)
    REFERENCES `post_rubrics` (`id`)
    ON DELETE SET NULL
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `note_rubrics`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `note_rubrics` ;

CREATE TABLE IF NOT EXISTS `note_rubrics` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_note_rubrics_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_note_rubrics_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `notes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `notes` ;

CREATE TABLE IF NOT EXISTS `notes` (
  `id` INT NOT NULL,
  `content` VARCHAR(255) NOT NULL,
  `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `note_rubric_id` INT NULL,
  `users_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_notes_note_rubrics1_idx` (`note_rubric_id` ASC) VISIBLE,
  INDEX `fk_notes_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_notes_note_rubrics1`
    FOREIGN KEY (`note_rubric_id`)
    REFERENCES `note_rubrics` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_notes_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SET SQL_MODE = '';
DROP USER IF EXISTS AiohttpAppAdmin;
SET SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE USER 'AiohttpAppAdmin' IDENTIFIED BY ''; 
GRANT ALL PRIVILEGES ON `aiohttp_app`.* TO 'AiohttpAppAdmin' WITH GRANT OPTION;
DROP USER 'AiohttpAppAdmin';

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
