# import bcrypt
# password = b"super secret password"
# # Hash a password for the first time, with a randomly-generated salt
# hashed = bcrypt.hashpw(password, bcrypt.gensalt())
# print(hashed)
# # Check that an unhashed password matches one that has previously been
# # hashed
# if bcrypt.checkpw(password, hashed):
#     print("It Matches!")
# else:
#     print("It Does not Match :(")


# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

# SAFE EXAMPLES. DO THIS!
# cursor.execute("SELECT admin FROM users WHERE username = %s'", (username, ));
# cursor.execute("SELECT admin FROM users WHERE username = %(username)s", {'username': username});


# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

# class MySqlConnectionExecutorError(Exception):
#     """
#     Raises error in `MySqlConnectionExecutor` class.
#     Error message at exception invokes is compulsory.
#     """
#
#
# class MySqlConnectionExecutor:
#     """
#     Contains and executes all queries besides db and tables initializing (dropping).
#     Implements all methods that interact with db (fetching, inserting, etc.).
#     Has convenient async context manager that handles db`s pool and implicit
#     (it does not need manually create connection and cursor in view functions) manages connection and cursor.
#
#     :raises: MySqlConnectionExecutorError
#     """
#
#     def __init__(self, pool: aiomysql.Pool = None) -> None:
#         self._pool = pool
#
#     # db methods
#     #
#
#     def __aenter__(self) -> aiomysql.Cursor:
#         if self._pool:
#             self._connection: aiomysql.Connection = await self._pool.acquire()
#             self._cursor: aiomysql.Cursor = await self._connection.cursor()
#             return self._cursor
#         elif self._pool is None:
#             message = (
#                 'MySqlConnectionExecutor was instantiated without `pool` argument. '
#                 'Using of contextmanager is impossible.'
#             )
#             raise MySqlConnectionExecutorError(message)
#         else:
#             message = (
#                 'MySqlConnectionExecutor was instantiated with incorrect type of `pool` argument. '
#                 '`pool` argument requires type: aiomysql.Pool. '
#                 'Using of contextmanager is impossible.'
#             )
#             raise MySqlConnectionExecutorError(message)
#
#     def __aexit__(self, exc_type, exc_val, exc_tb):
#         await self._cursor.close()
#         self._connection.close()
#         await self._connection.ensure_closed()
import asyncio
import aiomysql
from core.settings import get_config


# loop = asyncio.get_event_loop()
#
#
# async def init_mysql() -> None:
#     """ Create and set in app settings MySQL pool """
#     db_config = get_config()['mysql']
#
#     port: int = int(db_config['port'])
#
#     pool = await aiomysql.create_pool(
#         host=db_config['host'],
#         port=port,
#         user=db_config['user_name'],
#         password=db_config['user_password'],
#         db=db_config['database'],
#         loop=loop,
#         autocommit=True
#     )
#
#     async with pool.acquire() as connection:
#         async with connection.cursor() as cursor:
#             await cursor.execute('SELECT * FROM `posts`;')
#             res_1 = await cursor.fetchall()
#             res_2 = 0
#
#             print(res_1)
#             print(res_2)
#
#     pool.close()
#     await pool.wait_closed()
#
#
# loop.run_until_complete(init_mysql())


# from datetime import datetime
#
# import pydantic
#
#
# pydantic.BaseConfig.allow_population_by_field_name = True
# pydantic.BaseSettings.
#
# class UserCreation(pydantic.BaseModel):
#     title: str = pydantic.fields.Field(alias='t')
#
#
# try:
#     u = UserCreation(title='a', by_alias=False)
# except pydantic.ValidationError:
#     raise
# else:
#     print(u.dict(by_alias=True))
import aiomysql

# print(f"{'FROM':^20}|{'TO':^20}|{'WITH':^10}|{'':^20}")

# from core.database import db
#
# help(db)
