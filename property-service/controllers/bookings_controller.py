from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from database.connection import get_db
from models.property import Booking as BookingModel, BookingStatus, Property as PropertyModel
from schemas.property import BookingCreate, BookingResponse
from pydantic import BaseModel
from middleware.auth import get_current_user


router = APIRouter(prefix="/properties/bookings", tags=["bookings"])


class BookingListResponse(BaseModel):
    items: List[BookingResponse]


@router.get("/", response_model=List[BookingResponse])
def list_my_bookings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status_filter: Optional[BookingStatus] = Query(None)
):
    # Bookings where user is tenant
    tenant_q = db.query(BookingModel).filter(BookingModel.tenant_id == current_user["user_id"])
    # Or user is property owner
    owner_q = db.query(BookingModel).join(PropertyModel, PropertyModel.id == BookingModel.property_id).\
        filter(PropertyModel.owner_id == current_user["user_id"]) 

    if status_filter:
        tenant_q = tenant_q.filter(BookingModel.status == status_filter)
        owner_q = owner_q.filter(BookingModel.status == status_filter)

    items = tenant_q.union(owner_q).order_by(BookingModel.created_at.desc()).all()
    return [BookingResponse.model_validate(i, from_attributes=True) for i in items]


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # Authorization: tenant or owner
    is_tenant = booking.tenant_id == current_user["user_id"]
    prop = db.query(PropertyModel).filter(PropertyModel.id == booking.property_id).first()
    is_owner = prop and prop.owner_id == current_user["user_id"]
    if not (is_tenant or is_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    return BookingResponse.model_validate(booking, from_attributes=True)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Ensure property exists
    prop = db.query(PropertyModel).filter(PropertyModel.id == data.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    booking = BookingModel(
        property_id=data.property_id,
        tenant_id=current_user["user_id"],
        start_date=data.start_date,
        end_date=data.end_date,
        monthly_rent=prop.rent_amount or 0,
        security_deposit=prop.security_deposit or 0,
        status=BookingStatus.PENDING,
        notes=data.notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return BookingResponse.model_validate(booking, from_attributes=True)


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # Only tenant or owner can update
    is_tenant = booking.tenant_id == current_user["user_id"]
    prop = db.query(PropertyModel).filter(PropertyModel.id == booking.property_id).first()
    is_owner = prop and prop.owner_id == current_user["user_id"]
    if not (is_tenant or is_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    db.commit()
    db.refresh(booking)
    return BookingResponse.model_validate(booking, from_attributes=True)


@router.post("/{booking_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    is_tenant = booking.tenant_id == current_user["user_id"]
    prop = db.query(PropertyModel).filter(PropertyModel.id == booking.property_id).first()
    is_owner = prop and prop.owner_id == current_user["user_id"]
    if not (is_tenant or is_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    booking.status = BookingStatus.CANCELLED
    db.commit()
    return


@router.get("/available-slots", response_model=List[str])
def get_available_slots(
    property_id: int = Query(...),
    date: str = Query(...),
    db: Session = Depends(get_db),
):
    """Temporary stub for available slots; replace with real calendar logic."""
    # Generate hourly slots 9am-5pm
    try:
        _ = datetime.fromisoformat(date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD or ISO format.")
    slots = [f"{h:02d}:00" for h in range(9, 17)]
    return slots

