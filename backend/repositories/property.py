from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from decimal import Decimal

from .base import BaseRepository
from models.property import Property
from schemas.property import PropertyFilters


class PropertyRepository(BaseRepository[Property]):
    """Repository for Property model with search and filtering capabilities."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Property, db)
    
    async def get_active_properties(
        self,
        skip: int = 0,
        limit: int = 100,
        load_relationships: Optional[List[str]] = None
    ) -> List[Property]:
        """Get active properties."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"status": "active"},
            load_relationships=load_relationships or ["seller", "features"],
            order_by="created_at",
            order_desc=True
        )
    
    async def search_properties(
        self,
        filters: PropertyFilters,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Property], int]:
        """Advanced property search with filters."""
        # Build filter conditions
        filter_conditions = {"status": filters.status or "active"}
        
        # Price range filters
        if filters.min_price is not None:
            filter_conditions["price"] = {"operator": "gte", "value": filters.min_price}
        if filters.max_price is not None:
            # If min_price was already set, we need to handle this differently
            if "price" in filter_conditions:
                # We'll handle this in the raw query below
                pass
            else:
                filter_conditions["price"] = {"operator": "lte", "value": filters.max_price}
        
        # Other exact match filters
        if filters.bedrooms is not None:
            filter_conditions["bedrooms"] = filters.bedrooms
        if filters.bathrooms is not None:
            filter_conditions["bathrooms"] = filters.bathrooms
        if filters.property_type:
            filter_conditions["property_type"] = filters.property_type
        
        # Build query for complex conditions
        query = select(Property).options(
            selectinload(Property.seller),
            selectinload(Property.features)
        )
        
        conditions = [Property.status == (filters.status or "active")]
        
        # Price range conditions
        if filters.min_price is not None:
            conditions.append(Property.price >= filters.min_price)
        if filters.max_price is not None:
            conditions.append(Property.price <= filters.max_price)
        
        # Other conditions
        if filters.bedrooms is not None:
            conditions.append(Property.bedrooms == filters.bedrooms)
        if filters.bathrooms is not None:
            conditions.append(Property.bathrooms == filters.bathrooms)
        if filters.property_type:
            conditions.append(Property.property_type == filters.property_type)
        if filters.city:
            conditions.append(Property.city.ilike(f'%{filters.city}%'))
        if filters.state:
            conditions.append(Property.state.ilike(f'%{filters.state}%'))
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(Property.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and execute
        query = query.offset(skip).limit(limit).order_by(Property.created_at.desc())
        result = await self.db.execute(query)
        properties = result.scalars().all()
        
        return properties, total
    
    async def get_properties_by_seller(
        self,
        seller_id: int,
        include_inactive: bool = False
    ) -> List[Property]:
        """Get all properties for a specific seller."""
        filters = {"seller_id": seller_id}
        if not include_inactive:
            filters["status"] = "active"
        
        return await self.get_all(
            filters=filters,
            load_relationships=["features"],
            order_by="created_at",
            order_desc=True
        )
    
    async def get_properties_in_area(
        self,
        city: str,
        state: str,
        radius_km: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> List[Property]:
        """Get properties in a specific area."""
        filters = {
            "city": {"operator": "like", "value": city},
            "state": state,
            "status": "active"
        }
        
        # TODO: Add geographic radius search if lat/lng provided
        # This would require PostGIS or similar spatial extensions
        
        return await self.get_all(
            filters=filters,
            load_relationships=["seller", "features"]
        )
    
    async def get_similar_properties(
        self,
        property_id: int,
        limit: int = 5
    ) -> List[Property]:
        """Get properties similar to the given property."""
        # Get the reference property
        reference = await self.get_by_id(property_id)
        if not reference:
            return []
        
        # Find similar properties based on type, bedrooms, price range
        price_range = float(reference.price) * 0.2  # 20% price range
        min_price = float(reference.price) - price_range
        max_price = float(reference.price) + price_range
        
        query = select(Property).where(
            and_(
                Property.id != property_id,
                Property.status == "active",
                Property.property_type == reference.property_type,
                Property.city == reference.city,
                Property.price.between(Decimal(str(min_price)), Decimal(str(max_price)))
            )
        ).options(
            self.db.selectinload(Property.seller),
            self.db.selectinload(Property.features)
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_featured_properties(self, limit: int = 10) -> List[Property]:
        """Get featured properties (newest or with AI valuations)."""
        query = select(Property).where(
            Property.status == "active"
        ).options(
            self.db.selectinload(Property.seller),
            self.db.selectinload(Property.features)
        ).order_by(
            Property.ai_estimated_price.desc().nullslast(),
            Property.created_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_status(self, property_id: int, status: str) -> Optional[Property]:
        """Update property status."""
        return await self.update(property_id, status=status)
    
    async def add_images(self, property_id: int, image_urls: List[str]) -> Optional[Property]:
        """Add images to a property."""
        property_obj = await self.get_by_id(property_id)
        if not property_obj:
            return None
        
        current_images = property_obj.images or []
        updated_images = current_images + image_urls
        
        return await self.update(property_id, images=updated_images) 