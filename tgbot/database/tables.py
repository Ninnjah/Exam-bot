from datetime import datetime

from sqlalchemy import MetaData, Table, String, BigInteger, Column, DateTime

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("user_id", BigInteger(), primary_key=True),
    Column("firstname", String(), nullable=False),
    Column("lastname", String(), nullable=True),
    Column("username", String(), nullable=True),
    Column("created_on", DateTime(), default=datetime.now),
    Column("updated_on", DateTime(), default=datetime.now, onupdate=datetime.now)
)

pages = Table(
    "pages", metadata,
    Column("name", String(), primary_key=True),
    Column("link", String(), nullable=False),
    Column("created_on", DateTime(), default=datetime.now),
    Column("updated_on", DateTime(), default=datetime.now, onupdate=datetime.now)
)

assets = Table(
    "assets", metadata,
    Column("id", String(), primary_key=True),
    Column("file_id", String(), nullable=False),
    Column("created_on", DateTime(), default=datetime.now),
    Column("updated_on", DateTime(), default=datetime.now, onupdate=datetime.now)
)
