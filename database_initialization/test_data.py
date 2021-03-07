"""
Contains queries that generate test data.
"""


__all__ = ['query_to_create_users', 'query_to_create_post_rubrics', 'query_to_create_posts']


query_to_create_users = """
    INSERT INTO `users` (`id`, `login`, `password`)
    VALUES (101, 'user_number_one', 'user_number_one'),
           (102, 'user_number_two', 'user_number_two'),
           (103, 'user_number_three', 'user_number_three'),
           (104, 'user_number_four', 'user_number_four'),
           (105, 'user_number_five', 'user_number_five');
"""


query_to_create_post_rubrics = """
    INSERT INTO `post_rubrics` (`id`, `user_id`, `title`)
    VALUES (101, 1, 'Python'),
           (102, 1, 'C++'),
           (103, 1, 'Rust'),
           (104, 1, 'Golang'),
           (105, 1, 'Javascript');
"""


query_to_create_posts = """
    INSERT INTO `posts` (`user_id`, `title`, `content`, `rubric_id`)
    VALUES (101, 'Hello all Python-developers', 'GOOD LUCK!', 101),
           (102, 'Hello all Cpp-developers', 'GOOD LUCK!', 102),
           (103, 'Hello all Rust-developers', 'GOOD LUCK!', 103),
           (104, 'Hello all Golang-developers', 'GOOD LUCK!', 104),
           (105, 'Hello all Javascript-developers', 'GOOD LUCK!', 105);
"""
