from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Token
from src.repository.abstract_repos import TokenRepository
from src.schemas.tokens import TokenData


class DBTokenRepository(TokenRepository):

    async def add_token(self, body: TokenData, db: AsyncSession) -> Token:
        token = Token(**body.model_dump(exclude_unset=True))
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token

    async def get_token(self, token_str: str, db: AsyncSession) -> Token:
        stmt = select(Token).filter_by(token=token_str)
        result = await db.execute(stmt)
        token = result.scalar_one_or_none()
        return token

    async def block_token(self, token_str: str, db: AsyncSession) -> None:
        token = await self.get_token(token_str, db)
        if token:
            token.blocked = True
            await db.commit()
            await db.refresh(token)

    async def block_user_tokens(self, user_id: int, db: AsyncSession) -> None:
        stmt = select(Token).filter_by(user_id=user_id)
        result = await db.execute(stmt)
        tokens = result.scalars().all()
        for token in tokens:
            token.blocked = True
        await db.commit()

    async def token_is_blocked(self, token_str: str, db: AsyncSession) -> bool:
        token = await self.get_token(token_str, db)
        if not token:
            return False
        return token.blocked

    async def delete_expired(self, db: AsyncSession) -> None:
        now = datetime.utcnow()
        stmt = delete(Token).where(Token.expires < now)
        await db.execute(stmt)
        await db.commit()


token_repo: TokenRepository = DBTokenRepository()
