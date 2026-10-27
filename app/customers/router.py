from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.customers import service
from app.customers.schemas import CustomerIn, CustomerOut
from app.database import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerOut, status_code=201)
def create(data: CustomerIn, db: Session = Depends(get_db)):
    try:
        customer = service.create_customer(db, data)
        db.commit()
        return customer
    except service.EmailAlreadyUsed:
        db.rollback()
        raise HTTPException(409, "Ya existe un cliente con ese email")


@router.get("/{customer_id}", response_model=CustomerOut)
def get_one(customer_id: int, db: Session = Depends(get_db)):
    try:
        return service.get_customer(db, customer_id)
    except service.CustomerNotFound:
        raise HTTPException(404, "Cliente no encontrado")
