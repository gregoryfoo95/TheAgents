from typing import Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
import os
import uuid
from pathlib import Path

from repositories.property import PropertyRepository
from repositories.user import UserRepository
from schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyFilters,
    PropertyListResponse, Property as PropertySchema, PropertyImageUpload
)
from models.property import Property, PropertyFeature
from utilities.config import get_settings
from utilities.redis import redis_client, cache_result, invalidate_cache_pattern

settings = get_settings()


class PropertyService:
    """Service layer for property-related business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.property_repo = PropertyRepository(db)
        self.user_repo = UserRepository(db)

    async def create_property(
        self,
        property_data: PropertyCreate,
        seller_id: int
    ) -> PropertySchema:
        """Create a new property listing."""
        # Verify seller exists and is a seller
        seller = await self.user_repo.get_by_id(seller_id)
        if not seller or seller.user_type != "seller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only sellers can create property listings"
            )
        

        # Create property
        property_dict = property_data.model_dump(exclude={'features'})
        property_dict['seller_id'] = seller_id

        property_obj = await self.property_repo.create(**property_dict)

        # Create features if provided
        if property_data.features:
            for feature_data in property_data.features:
                await self.db.execute(
                    PropertyFeature.__table__.insert().values(
                        property_id=property_obj.id,
                        **feature_data.model_dump()
                    )
                )
            await self.db.commit()

        # Invalidate property caches
        await self._invalidate_property_caches()

        # Load relationships and return
        property_with_relations = await self.property_repo.get_by_id(
            property_obj.id,
            load_relationships=["seller", "features"]
        )

        return PropertySchema.model_validate(property_with_relations)

    async def get_property_by_id(self, property_id: int) -> Optional[PropertySchema]:
        """Get property by ID with caching."""
        cache_key = f"property:{property_id}"

        # Try cache first
        cached_property = await redis_client.get_json(cache_key)
        if cached_property:
            return PropertySchema(**cached_property)

        # Get from database
        property_obj = await self.property_repo.get_by_id(
            property_id,
            load_relationships=["seller", "features"]
        )

        if not property_obj:
            return None

        property_schema = PropertySchema.model_validate(property_obj)

        # Cache for 5 minutes
        await redis_client.set_json(cache_key, property_schema.model_dump(), expire=300)

        return property_schema

    async def search_properties(
        self,
        filters: PropertyFilters,
        page: int = 1,
        size: int = 20
    ) -> PropertyListResponse:
        """Search properties with filters and pagination."""
        # Validate page parameters
        if page < 1:
            page = 1
        if size < 1 or size > settings.max_page_size:
            size = settings.default_page_size

        skip = (page - 1) * size

        # Create cache key from filters
        cache_key = f"properties_search:{hash(str(filters.model_dump()))}:{page}:{size}"

        # Try cache first (temporarily disabled for debugging)
        # cached_result = await redis_client.get_json(cache_key)
        # if cached_result:
        #     return PropertyListResponse(**cached_result)

        # Get from database
        properties, total = await self.property_repo.search_properties(
            filters=filters,
            skip=skip,
            limit=size
        )

        # Convert to schemas
        property_schemas = [PropertySchema.model_validate(prop) for prop in properties]

        # Calculate pagination
        total_pages = (total + size - 1) // size

        result = PropertyListResponse(
            items=property_schemas,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )

        # Cache for 5 minutes (temporarily disabled for debugging)
        # await redis_client.set_json(cache_key, result.model_dump(), expire=300)

        return result

    async def update_property(
        self,
        property_id: int,
        property_data: PropertyUpdate,
        user_id: int
    ) -> Optional[PropertySchema]:
        """Update property (only by owner)."""
        # Check if property exists and user is the owner
        property_obj = await self.property_repo.get_by_id(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        if property_obj.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own properties"
            )

        # Update property
        update_data = property_data.model_dump(exclude_unset=True)
        updated_property = await self.property_repo.update(property_id, **update_data)

        if not updated_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        # Invalidate caches
        await self._invalidate_property_caches()
        await redis_client.delete(f"property:{property_id}")

        # Return updated property with relationships
        property_with_relations = await self.property_repo.get_by_id(
            property_id,
            load_relationships=["seller", "features"]
        )

        return PropertySchema.model_validate(property_with_relations)

    async def delete_property(self, property_id: int, user_id: int) -> bool:
        """Delete property (only by owner)."""
        # Check ownership
        property_obj = await self.property_repo.get_by_id(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        if property_obj.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own properties"
            )

        # Delete property
        success = await self.property_repo.delete(property_id)

        if success:
            # Clean up caches
            await self._invalidate_property_caches()
            await redis_client.delete(f"property:{property_id}")

        return success

    async def get_properties_by_seller(
        self,
        seller_id: int,
        include_inactive: bool = False
    ) -> List[PropertySchema]:
        """Get all properties for a seller."""
        properties = await self.property_repo.get_properties_by_seller(
            seller_id=seller_id,
            include_inactive=include_inactive
        )
        return [PropertySchema.model_validate(prop) for prop in properties]

    async def upload_property_images(
        self,
        property_id: int,
        files: List[UploadFile],
        user_id: int
    ) -> PropertyImageUpload:
        """Upload images for a property."""
        # Check ownership
        property_obj = await self.property_repo.get_by_id(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        if property_obj.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload images to your own properties"
            )

        # Validate files
        image_urls = []
        for file in files:
            # Check file type
            if file.content_type not in settings.allowed_image_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file.content_type} not allowed for images"
                )

            # Check file size
            file_size = 0
            content = await file.read()
            file_size = len(content)

            if file_size > settings.max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size {file_size} exceeds maximum allowed size"
                )

            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = f"uploads/properties/{property_id}/{unique_filename}"

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(content)

            image_urls.append(f"/uploads/properties/{property_id}/{unique_filename}")

        # Update property with new images
        updated_property = await self.property_repo.add_images(property_id, image_urls)

        if not updated_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        # Invalidate caches
        await redis_client.delete(f"property:{property_id}")

        return PropertyImageUpload(
            property_id=property_id,
            image_urls=image_urls,
            total_images=len(updated_property.images or [])
        )

    async def get_featured_properties(self, limit: int = 10) -> List[PropertySchema]:
        """Get featured properties."""
        cache_key = f"properties:featured:{limit}"

        # Try cache first
        cached_properties = await redis_client.get_json(cache_key)
        if cached_properties:
            return [PropertySchema(**prop) for prop in cached_properties]

        # Get from database
        properties = await self.property_repo.get_featured_properties(limit)
        property_schemas = [PropertySchema.model_validate(prop) for prop in properties]

        # Cache for 10 minutes
        await redis_client.set_json(
            cache_key,
            [prop.model_dump() for prop in property_schemas],
            expire=600
        )

        return property_schemas

    async def get_similar_properties(
        self,
        property_id: int,
        limit: int = 5
    ) -> List[PropertySchema]:
        """Get properties similar to the given property."""
        cache_key = f"properties:similar:{property_id}:{limit}"

        # Try cache first
        cached_properties = await redis_client.get_json(cache_key)
        if cached_properties:
            return [PropertySchema(**prop) for prop in cached_properties]

        # Get from database
        properties = await self.property_repo.get_similar_properties(property_id, limit)
        property_schemas = [PropertySchema.model_validate(prop) for prop in properties]

        # Cache for 30 minutes
        await redis_client.set_json(
            cache_key,
            [prop.model_dump() for prop in property_schemas],
            expire=1800
        )

        return property_schemas

    async def update_property_status(
        self,
        property_id: int,
        status: str,
        user_id: int
    ) -> Optional[PropertySchema]:
        """Update property status (by owner only)."""
        # Check ownership
        property_obj = await self.property_repo.get_by_id(property_id)
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        if property_obj.seller_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own properties"
            )

        # Update status
        updated_property = await self.property_repo.update_status(property_id, status)

        if not updated_property:
            return None

        # Invalidate caches
        await self._invalidate_property_caches()
        await redis_client.delete(f"property:{property_id}")

        return PropertySchema.model_validate(updated_property)

    async def _invalidate_property_caches(self) -> None:
        """Invalidate property-related caches."""
        patterns = [
            "properties_search:*",
            "properties:featured:*",
            "properties:similar:*",
            "properties:active:*"
        ]

        for pattern in patterns:
            await invalidate_cache_pattern(pattern) 