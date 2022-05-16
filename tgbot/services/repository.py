from typing import Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.engine import AsyncConnection

from tgbot.database.tables import users, pages


class Repo:
    """Db abstraction layer"""

    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    # users
    async def add_user(
            self,
            user_id: int,
            firstname: str,
            lastname: Optional[str],
            username: Optional[str]
    ) -> None:
        """Store user in DB, ignore duplicates"""
        stmt = insert(users).values(
            user_id=user_id,
            firstname=firstname,
            lastname=lastname,
            username=username
        ).on_conflict_do_nothing()

        await self.conn.execute(stmt)
        await self.conn.commit()
        return

    async def get_user(self, user_id: int):
        """Returns user from DB by user id"""
        stmt = users.select().where(
            users.c.user_id == user_id
        )

        res = await self.conn.execute(stmt)

        try:
            return res.mappings().one()

        except NoResultFound:
            return

    async def list_users(self) -> list:
        """List all bot users"""
        stmt = users.select()

        res = await self.conn.execute(stmt)
        return res.mappings().all()

    async def add_page(self, name: str, link: str) -> None:
        """Store page in DB, ignore duplicates"""
        stmt = insert(pages).values(
            name=name,
            link=link
        ).on_conflict_do_nothing()

        await self.conn.execute(stmt)
        await self.conn.commit()
        return

    async def get_page(self, name: str) -> Optional[str]:
        """Returns page link from DB"""
        stmt = pages.select().where(
            pages.c.name == name
        )

        res = await self.conn.execute(stmt)

        try:
            return res.mappings().one()

        except NoResultFound:
            return None
