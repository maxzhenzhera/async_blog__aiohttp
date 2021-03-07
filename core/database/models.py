"""
Contains classes that implement the database objects. `Database` and `TableName` contain only sql queries.

.. class:: Database
    Contains queries that create/drop database, database`s user

.. class:: TableUsers
    Contains sql queries that implement this entity (create/drop)
.. class:: ViewModerators
    Contains sql queries that implement this entity (create/drop)
.. class:: TablePostRubrics
    Contains sql queries that implement this entity (create/drop)
.. class:: TablePosts
    Contains sql queries that implement this entity (create/drop)
.. class:: TableNoteRubrics
    Contains sql queries that implement this entity (create/drop)
.. class:: TableNotes
    Contains sql queries that implement this entity (create/drop)

.. const:: tables
    Contains all database tables in order (ParentTable, ChildTable)
"""

__all__ = ['Database', 'tables']


class Database:
    """ Implement app database """
    # DB
    create_database = """
        DROP DATABASE IF EXISTS {db_name};
        CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET utf8;
    """
    drop_database = "DROP SCHEMA IF EXISTS {db_name};"
    use_database = "USE {db_name};"

    # DB user
    create_user = """
        DROP USER IF EXISTS {user_name}@{host};
        CREATE USER IF NOT EXISTS {user_name}@{host} IDENTIFIED BY '{user_password}';
        GRANT ALL PRIVILEGES ON {db_name}.* TO {user_name}@{host};
    """
    drop_user = "DROP USER IF EXISTS {user_name};"


class TableUsers:
    """ Implement `users` table """
    create_table = """
        DROP TABLE IF EXISTS `users`;
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
    """
    drop_table = "DROP TABLE IF EXISTS `users`;"


class ViewModerators:
    """ Implement `moderators` table (by view) """
    create_table = """
    DROP VIEW IF EXISTS `moderators`;
    CREATE VIEW `moderators` AS 
        SELECT * FROM `users` WHERE `is_moderator` = TRUE;
    """

    drop_table = "DROP VIEW IF EXISTS `moderators`;"


class TablePostRubrics:
    """ Implement `post_rubrics` table """
    create_table = """
        DROP TABLE IF EXISTS `post_rubrics`;
        CREATE TABLE IF NOT EXISTS `post_rubrics` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `title` VARCHAR(255) NOT NULL,
            `user_id` INT NULL,
            PRIMARY KEY (`id`),
            FOREIGN KEY (`user_id`)
                REFERENCES `users` (`id`)
                ON DELETE SET NULL ON UPDATE NO ACTION
        )  ENGINE=INNODB;
    """
    drop_table = "DROP TABLE IF EXISTS `post_rubrics`;"


class TablePosts:
    """ Implement `posts` table """
    create_table = """
        DROP TABLE IF EXISTS `posts`;
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
    """
    drop_table = "DROP TABLE IF EXISTS `posts`;"


class TableNoteRubrics:
    """ Implement `note_rubrics` table """
    create_table = """
        DROP TABLE IF EXISTS `note_rubrics`;
        CREATE TABLE IF NOT EXISTS `note_rubrics` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `title` VARCHAR(255) NOT NULL,
            `user_id` INT NOT NULL,
            PRIMARY KEY (`id`),
            FOREIGN KEY (`user_id`)
                REFERENCES `users` (`id`)
                ON DELETE CASCADE ON UPDATE NO ACTION
        )  ENGINE=INNODB;
    """
    drop_table = "DROP TABLE IF EXISTS `note_rubrics`;"


class TableNotes:
    """ Implement `notes` table """
    create_table = """
        DROP TABLE IF EXISTS `notes`;
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
    """
    drop_table = "DROP TABLE IF EXISTS `notes`;"


# ------------------------- It`s compulsory to keep order like: -------------------------
# TableParent, TableChild ...
# This order counts in `init_db.py` when tables create or drop.
tables: tuple = (
    TableUsers, ViewModerators,
    TablePostRubrics,
    TablePosts,
    TableNoteRubrics,
    TableNotes,
)
# ------------------------- ||||||||||||||||||||||||||||||||||| -------------------------
