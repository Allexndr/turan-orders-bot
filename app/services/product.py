from sqlalchemy import select

from app.database import autosession
from app.models import Product

 
async def list_products(limit: int = 50):
    async with autosession() as session:
        result = await session.execute(select(Product).limit(limit))
        return result.scalars().all() 