from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from utilities.database import get_async_db
from services.property_service import PropertyService
from schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyFilters,
    Property as PropertySchema, PropertyListResponse
)
from schemas.user import User as UserSchema
from schemas.base import SuccessResponse
from middleware.auth import get_current_active_user, require_seller

property_router = APIRouter(prefix="/api/properties", tags=["properties"])



@property_router.get(
    "/",
    response_model=PropertyListResponse,
    summary="Search properties",
    description="Search and filter properties with pagination"
)
async def search_properties(
    # Property type filter
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    
    # Price filters
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    
    # Room filters
    bedrooms: Optional[int] = Query(None, ge=0, le=20, description="Number of bedrooms"),
    bathrooms: Optional[int] = Query(None, ge=0, le=20, description="Number of bathrooms"),
    
    # Size filters
    min_square_feet: Optional[int] = Query(None, gt=0, description="Minimum square footage"),
    max_square_feet: Optional[int] = Query(None, gt=0, description="Maximum square footage"),
    
    # Location filters
    city: Optional[str] = Query(None, description="City"),
    state: Optional[str] = Query(None, description="State"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
    
    # Status filter
    status: Optional[str] = Query("active", description="Property status"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    
    db: AsyncSession = Depends(get_async_db)
):
    """Search properties with filters and pagination."""
    try:
        # Create filters object
        filters = PropertyFilters(
            property_type=property_type,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            min_square_feet=min_square_feet,
            max_square_feet=max_square_feet,
            city=city,
            state=state,
            zip_code=zip_code,
            status=status
        )
        
        property_service = PropertyService(db)
        result = await property_service.search_properties(filters, page, size)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@property_router.get(
    "/featured",
    response_model=List[PropertySchema],
    summary="Get featured properties",
    description="Get a list of featured properties"
)
async def get_featured_properties(
    limit: int = Query(10, ge=1, le=50, description="Number of properties to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get featured properties."""
    try:
        property_service = PropertyService(db)
        properties = await property_service.get_featured_properties(limit)
        return properties
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get featured properties: {str(e)}"
        )


@property_router.get(
    "/{property_id}",
    response_model=PropertySchema,
    summary="Get property by ID",
    description="Get detailed information about a specific property"
)
async def get_property_by_id(
    property_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get property by ID."""
    try:
        property_service = PropertyService(db)
        property_obj = await property_service.get_property_by_id(property_id)
        
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        return property_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property: {str(e)}"
        )


@property_router.get(
    "/{property_id}/similar",
    response_model=List[PropertySchema],
    summary="Get similar properties",
    description="Get properties similar to the specified property"
)
async def get_similar_properties(
    property_id: int,
    limit: int = Query(5, ge=1, le=20, description="Number of similar properties to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get properties similar to the given property."""
    try:
        property_service = PropertyService(db)
        properties = await property_service.get_similar_properties(property_id, limit)
        return properties
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get similar properties: {str(e)}"
        )


@property_router.post(
    "/",
    response_model=PropertySchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create property listing",
    description="Create a new property listing (sellers only)"
)
async def create_property(
    property_data: PropertyCreate,
    current_user: UserSchema = Depends(require_seller),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new property listing."""
    try:
        property_service = PropertyService(db)
        property_obj = await property_service.create_property(property_data, current_user.id)
        return property_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create property: {str(e)}"
        )


@property_router.put(
    "/{property_id}",
    response_model=PropertySchema,
    summary="Update property",
    description="Update property information (owner only)"
)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update property information."""
    try:
        property_service = PropertyService(db)
        property_obj = await property_service.update_property(
            property_id, property_data, current_user.id
        )
        return property_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property: {str(e)}"
        )


@property_router.delete(
    "/{property_id}",
    response_model=SuccessResponse,
    summary="Delete property",
    description="Delete property listing (owner only)"
)
async def delete_property(
    property_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete property listing."""
    try:
        property_service = PropertyService(db)
        success = await property_service.delete_property(property_id, current_user.id)
        
        if success:
            return SuccessResponse(message="Property deleted successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete property"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete property: {str(e)}"
        )


@property_router.patch(
    "/{property_id}/status",
    response_model=PropertySchema,
    summary="Update property status",
    description="Update property status (owner only)"
)
async def update_property_status(
    property_id: int,
    status: str = Query(..., description="New property status"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update property status."""
    try:
        property_service = PropertyService(db)
        property_obj = await property_service.update_property_status(
            property_id, status, current_user.id
        )
        
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        return property_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property status: {str(e)}"
        )


@property_router.post(
    "/{property_id}/images",
    response_model=PropertySchema, # This response model was not in the new_code, but should be updated for consistency
    summary="Upload property images",
    description="Upload images for a property (owner only)"
)
async def upload_property_images(
    property_id: int,
    files: List[UploadFile] = File(..., description="Image files to upload"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Upload images for a property."""
    try:
        # Validate that files are provided
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        # Limit number of files
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per upload"
            )
        
        property_service = PropertyService(db)
        result = await property_service.upload_property_images(
            property_id, files, current_user.id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload images: {str(e)}"
        )


@property_router.get(
    "/seller/{seller_id}",
    response_model=List[PropertySchema],
    summary="Get properties by seller",
    description="Get all properties listed by a specific seller"
)
async def get_properties_by_seller(
    seller_id: int,
    include_inactive: bool = Query(False, description="Include inactive properties"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get properties by seller."""
    try:
        # Only allow sellers to see their own inactive properties
        if include_inactive and current_user.id != seller_id:
            include_inactive = False
        
        property_service = PropertyService(db)
        properties = await property_service.get_properties_by_seller(
            seller_id, include_inactive
        )
        return properties
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get properties: {str(e)}"
        )


@property_router.get(
    "/my/listings",
    response_model=List[PropertySchema],
    summary="Get current user's properties",
    description="Get all properties listed by the current user"
)
async def get_my_properties(
    include_inactive: bool = Query(True, description="Include inactive properties"),
    current_user: UserSchema = Depends(require_seller),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current user's property listings."""
    try:
        property_service = PropertyService(db)
        properties = await property_service.get_properties_by_seller(
            current_user.id, include_inactive
        )
        return properties
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get properties: {str(e)}"
        ) 