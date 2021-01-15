"""
Initialize (create db, tables, new role) and implement deleting all this stuff.
As we don`t use ORM like SQLAlchemy, most of the needed SQL code is saved in a particular directory.
"""

# from core.db import question, choice
from core.settings import BASE_DIR, get_config


USER_CONFIG_PATH = BASE_DIR / 'config' / 'config.ini'
USER_CONFIG = get_config()

# TEST_CONFIG_PATH = BASE_DIR / 'config' / 'test_config.ini'
# TEST_CONFIG = get_config()


def setup_db(config):

    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']
    db_host = config['host']

    conn = admin_engine.connect()

    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (db_user, db_host, db_pass))

    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))


def teardown_db(config):

    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("""
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = '%s'
        AND pid <> pg_backend_pid();""" % db_name)
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()


def create_tables(engine=test_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[question, choice])


def drop_tables(engine=test_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[question, choice])


if __name__ == '__main__':
    pass
    # setup_db(USER_CONFIG['postgres'])
    # create_tables(engine=user_engine)

    # --------------------------------------------------
    # --------------------------------------------------
    # --------------------------------------------------

    # drop_tables()
    # teardown_db(USER_CONFIG['postgres'])

    # --------------------------------------------------
