from datetime import datetime

from sqlalchemy import MetaData, Table, BigInteger, Boolean, Column, DateTime, Float, Integer, String

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

user_statistics = Table(
    "user_statistics", metadata,
    Column("id", Integer(), primary_key=True, auto_increment=True),
    Column("user_id", BigInteger(), nullable=False),
    Column("ticket_number", Integer(), nullable=False),
    Column("ticket_category", String(), nullable=False),
    Column("tip_count", Integer(), nullable=False),
    Column("questions", Integer(), nullable=False),
    Column("score", Integer(), nullable=False),
    Column("correctness", Float(), nullable=False),
    Column("success", Boolean(), nullable=False),
    Column("time_spent", DateTime(), nullable=False),
    Column("start_time", DateTime(), nullbale=False),
    Column("created_on", DateTime(), default=datetime.now),
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

config = Table(
    "config", metadata,
    Column("parameter", String(), primary_key=True),
    Column("value", String(), nullable=False),
    Column("created_on", DateTime(), default=datetime.now),
    Column("updated_on", DateTime(), default=datetime.now, onupdate=datetime.now)
)
