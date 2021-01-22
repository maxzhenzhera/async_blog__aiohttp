""" Db tables """


class TableUsers:
    """ Implement `users` table """
    create_table = (
        "DROP TABLE IF EXISTS `users`;          "
        "CREATE TABLE IF NOT EXISTS `users` (   "
        "    `id` INT NOT NULL AUTO_INCREMENT,  "
        "    `login` VARCHAR(255) NOT NULL,     "
        "    `password` VARCHAR(255) NOT NULL,  "
        "    `is_admin` TINYINT NOT NULL,       "
        "    PRIMARY KEY (`id`)                 "
        ")  ENGINE=INNODB;                      "
    )
    drop_table = "DROP TABLE IF EXISTS `users` ;"


class TablePostRubrics:
    """ Implement `post_rubrics` table """
    create_table = (
        "DROP TABLE IF EXISTS `post_rubrics`;           "
        "CREATE TABLE IF NOT EXISTS `post_rubrics` (    "
        "    `id` INT NOT NULL AUTO_INCREMENT,          "
        "    `title` VARCHAR(255) NOT NULL,             "
        "    `user_id` INT NULL,                        "
        "    PRIMARY KEY (`id`),                        "
        "    FOREIGN KEY (`user_id`)                    "
        "        REFERENCES `users` (`id`)              "
        "        ON DELETE SET NULL ON UPDATE NO ACTION "
        ")  ENGINE=INNODB;                              "
    )
    drop_table = "DROP TABLE IF EXISTS `post_rubrics`;"


class TablePosts:
    """ Implement `posts` table """
    create_table = (
        "DROP TABLE IF EXISTS `posts`;                                                              "
        "CREATE TABLE IF NOT EXISTS `posts` (                                                       "
        "    `id` INT NOT NULL AUTO_INCREMENT,                                                      "
        "    `title` VARCHAR(255) NOT NULL,                                                         "
        "    `content` BLOB NOT NULL,                                                               "
        "    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,                            "
        "    `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
        "    `user_id` INT NULL,                                                                    "
        "    `post_rubric_id` INT NULL,                                                             "
        "    PRIMARY KEY (`id`),                                                                    "
        "    FULLTEXT ( `title` , `content` ),                                                      "
        "    FOREIGN KEY (`user_id`)                                                                " 
        "        REFERENCES `users` (`id`)                                                          "
        "        ON DELETE SET NULL ON UPDATE NO ACTION,                                            "    
        "    FOREIGN KEY (`post_rubric_id`)                                                         "
        "        REFERENCES `post_rubrics` (`id`)                                                   "
        "        ON DELETE SET NULL ON UPDATE NO ACTION                                             "
        ")  ENGINE=INNODB;                                                                          "
    )
    drop_table = "DROP TABLE IF EXISTS `posts`;"


class TableNoteRubrics:
    """ Implement `note_rubrics` table """
    create_table = (
        "DROP TABLE IF EXISTS `note_rubrics`;           "
        "CREATE TABLE IF NOT EXISTS `note_rubrics` (    "
        "    `id` INT NOT NULL AUTO_INCREMENT,          "
        "    `title` VARCHAR(255) NOT NULL,             "
        "    `user_id` INT NOT NULL,                    "
        "    PRIMARY KEY (`id`),                        "
        "    FOREIGN KEY (`user_id`)                    "
        "        REFERENCES `users` (`id`)              "
        "        ON DELETE CASCADE ON UPDATE NO ACTION  "
        ")  ENGINE=INNODB;                              "
    )
    drop_table = (
        "DROP TABLE IF EXISTS `note_rubrics`;"
    )


class TableNotes:
    """ Implement `notes` table """
    create_table = (
        "DROP TABLE IF EXISTS `notes`;                                                              "
        "CREATE TABLE IF NOT EXISTS `notes` (                                                       "
        "    `id` INT NOT NULL,                                                                     "
        "    `content` VARCHAR(255) NOT NULL,                                                       "
        "    `created_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,                            "
        "    `edited_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
        "    `note_rubric_id` INT NULL,                                                             "
        "    `users_id` INT NOT NULL,                                                               "
        "    PRIMARY KEY (`id`),                                                                    "
        "    FOREIGN KEY (`note_rubric_id`)                                                         "
        "        REFERENCES `note_rubrics` (`id`)                                                   "
        "        ON DELETE CASCADE ON UPDATE NO ACTION,                                             "
        "    FOREIGN KEY (`users_id`)                                                               "
        "        REFERENCES `users` (`id`)                                                          "
        "        ON DELETE CASCADE ON UPDATE NO ACTION                                              "
        ")  ENGINE=INNODB;                                                                          "
    )
    drop_table = (
        "DROP TABLE IF EXISTS `notes`;"
    )
