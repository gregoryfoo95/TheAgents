from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import os
import uuid

from database.connection import get_db
from models.property import Property as PropertyModel, PropertyImage as PropertyImageModel, PropertyStatus, PropertyType
from schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse
from pydantic import BaseModel
from middleware.auth import get_current_user


router = APIRouter(prefix="/properties", tags=["properties"])


class PropertyListResponse(BaseModel):
    items: List[PropertyResponse]
    total: int
    page: int
    size: int
    total_pages: int


@router.get("/", response_model=PropertyListResponse)
def list_properties(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    property_type: Optional[PropertyType] = Query(None),
    bedrooms: Optional[int] = Query(None, ge=0),
    bathrooms: Optional[int] = Query(None, ge=0),
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    status: Optional[PropertyStatus] = Query(None),
):
    query = db.query(PropertyModel)

    if city:
        query = query.filter(PropertyModel.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(PropertyModel.state.ilike(f"%{state}%"))
    if property_type:
        query = query.filter(PropertyModel.property_type == property_type)
    if bedrooms is not None:
        query = query.filter(PropertyModel.bedrooms >= bedrooms)
    if bathrooms is not None:
        query = query.filter(PropertyModel.bathrooms >= bathrooms)
    if min_price is not None:
        query = query.filter(PropertyModel.rent_amount >= min_price)
    if max_price is not None:
        query = query.filter(PropertyModel.rent_amount <= max_price)
    if status:
        query = query.filter(PropertyModel.status == status)

    total = query.count()
    items = (
        query.order_by(PropertyModel.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    total_pages = (total + size - 1) // size
    return PropertyListResponse(
        items=[PropertyResponse.model_validate(i, from_attributes=True) for i in items],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return PropertyResponse.model_validate(prop, from_attributes=True)


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    prop = PropertyModel(
        owner_id=current_user["user_id"],
        title=data.title,
        description=data.description,
        property_type=data.property_type,
        address=data.address,
        city=data.city,
        state=data.state,
        country=data.country,
        postal_code=data.postal_code,
        bedrooms=data.bedrooms,
        bathrooms=data.bathrooms,
        square_feet=data.square_feet,
        rent_amount=data.rent_amount,
        security_deposit=data.security_deposit,
        amenities=data.amenities,
        features=data.features,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return PropertyResponse.model_validate(prop, from_attributes=True)


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    prop = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    if prop.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return PropertyResponse.model_validate(prop, from_attributes=True)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    prop = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    if prop.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    db.delete(prop)
    db.commit()
    return


@router.post("/{property_id}/images")
def upload_images(
    property_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    prop = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    if prop.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    os.makedirs("uploads", exist_ok=True)
    uploaded = []
    for f in files:
        ext = os.path.splitext(f.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join("uploads", unique_name)
        with open(file_path, "wb") as out:
            out.write(f.file.read())

        image = PropertyImageModel(
            property_id=property_id,
            filename=unique_name,
            original_filename=f.filename,
            file_path=file_path,
            file_size=0,
            content_type=f.content_type or "application/octet-stream",
            is_primary=False,
        )
        db.add(image)
        uploaded.append(unique_name)

    db.commit()
    return {"uploaded_images": uploaded}


@router.get("/my/listings", response_model=List[PropertyResponse])
def my_properties(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    items = (
        db.query(PropertyModel)
        .filter(PropertyModel.owner_id == current_user["user_id"]) 
        .order_by(PropertyModel.created_at.desc())
        .all()
    )
    return [PropertyResponse.model_validate(i, from_attributes=True) for i in items]

