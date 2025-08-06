from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, delete, func, and_
from typing import Optional, List, Dict, Any, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from utilities.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(
        self,
        id: int,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Get a single record by ID with optional relationship loading."""
        query = select(self.model).where(self.model.id == id)

        if load_relationships:
            for relationship in load_relationships:
                query = query.options(selectinload(getattr(self.model, relationship)))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(
        self,
        field_name: str,
        value: Any,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Get a single record by any field."""
        query = select(self.model).where(getattr(self.model, field_name) == value)

        if load_relationships:
            for relationship in load_relationships:
                query = query.options(selectinload(getattr(self.model, relationship)))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        load_relationships: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Get multiple records with filtering, pagination, and ordering."""
        query = select(self.model)

        # Apply filters
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    elif isinstance(value, dict) and 'operator' in value:
                        # Support for complex operators
                        field_attr = getattr(self.model, field)
                        operator = value['operator']
                        val = value['value']

                        if operator == 'gte':
                            conditions.append(field_attr >= val)
                        elif operator == 'lte':
                            conditions.append(field_attr <= val)
                        elif operator == 'like':
                            conditions.append(field_attr.ilike(f'%{val}%'))
                        elif operator == 'not_equal':
                            conditions.append(field_attr != val)
                    else:
                        conditions.append(getattr(self.model, field) == value)

            if conditions:
                query = query.where(and_(*conditions))

        # Apply relationships loading
        if load_relationships:
            for relationship in load_relationships:
                query = query.options(selectinload(getattr(self.model, relationship)))

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        query = select(func.count(self.model.id))

        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)

            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar()

    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(
        self,
        id: int,
        **kwargs
    ) -> Optional[ModelType]:
        """Update a record by ID."""
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def bulk_create(self, data: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in bulk."""
        objects = [self.model(**item) for item in data]
        self.db.add_all(objects)
        await self.db.commit()

        # Refresh all objects to get their IDs
        for obj in objects:
            await self.db.refresh(obj)

        return objects

    async def exists(self, **kwargs) -> bool:
        """Check if a record exists with the given criteria."""
        conditions = []
        for field, value in kwargs.items():
            if hasattr(self.model, field):
                conditions.append(getattr(self.model, field) == value)

        if not conditions:
            return False

        query = select(func.count(self.model.id)).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar() > 0
