from datetime import datetime
from typing import Optional

from sqlalchemy import select, inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.engine import AsyncConnection

from tgbot.database.tables import assets, users, pages, config, user_statistics


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
        """Store user in DB, on conflict updates user information"""
        primary_keys = [key.name for key in inspect(users).primary_key]

        stmt = insert(users).values(
            user_id=user_id,
            firstname=firstname,
            lastname=lastname,
            username=username
        ).on_conflict_do_update(
            index_elements=primary_keys, set_={
                "firstname": firstname,
                "lastname": lastname,
                "username": username
            }
        )

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
        stmt = users.select().order_by(users.c.created_on)

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

    async def add_asset(self, asset_id: str, file_id: str) -> None:
        """Store asset in DB, ignore duplicates"""
        stmt = insert(assets).values(
            id=asset_id,
            file_id=file_id
        ).on_conflict_do_nothing()

        await self.conn.execute(stmt)
        await self.conn.commit()
        return

    async def get_asset(self, asset_id: str):
        """Returns asset from DB"""
        stmt = assets.select().where(
            assets.c.id == asset_id
        )

        res = await self.conn.execute(stmt)

        try:
            return res.mappings().one()

        except NoResultFound:
            return None

    async def add_config(self, **kwargs):
        primary_keys = [key.name for key in inspect(config).primary_key]

        stmt = insert(config).values(
            **kwargs
        ).on_conflict_do_update(
            index_elements=primary_keys, set_=kwargs
        )

        await self.conn.execute(stmt)
        await self.conn.commit()
        return

    async def get_config(self, parameter: str):
        stmt = select(config).where(
            config.c.parameter == parameter
        )

        res = await self.conn.execute(stmt)

        try:
            return res.mappings().one()

        except NoResultFound:
            return

    async def add_statistic(
            self,
            user_id: int,
            ticket_number: int,
            ticket_category: str,
            tip_count: int,
            questions: int,
            score: int,
            success: bool,
            time_spent: float,
            start_time: datetime
    ):
        stmt = insert(user_statistics).values(
            user_id=user_id,
            ticket_number=ticket_number,
            ticket_category=ticket_category,
            tip_count=tip_count,
            questions=questions,
            score=score,
            correctness=score / questions * 100,
            success=success,
            time_spent=time_spent,
            start_time=start_time
        )

        await self.conn.execute(stmt)
        await self.conn.commit()
        return

    async def list_statistics(self):
        """Returns all statistics from DB"""
        stmt = select(user_statistics).order_by(user_statistics.c.created_on)

        res = await self.conn.execute(stmt)
        return res.mappings().all()
