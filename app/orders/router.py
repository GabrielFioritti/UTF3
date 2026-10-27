from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.customers.service import CustomerNotFound
from app.database import get_db
from app.orders import service
from app.orders.schemas import OrderIn, OrderOut
from app.products.service import InsufficientStock, ProductNotFound

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create(data: OrderIn, db: Session = Depends(get_db)):
    try:
        order = service.create_order(db, data)
        db.commit()  # único punto de commit: todo o nada
        return order
    except CustomerNotFound:
        db.rollback()
        raise HTTPException(404, "Cliente no encontrado")
    except ProductNotFound as e:
        db.rollback()
        raise HTTPException(404, f"Producto {e} no encontrado")
    except InsufficientStock as e:
        db.rollback()  # deshace también el stock ya descontado de otros ítems
        raise HTTPException(409, f"Stock insuficiente para el producto {e}")


@router.get("", response_model=list[OrderOut])
def list_all(db: Session = Depends(get_db)):
    return service.list_orders(db)


@router.get("/{order_id}", response_model=OrderOut)
def get_one(order_id: int, db: Session = Depends(get_db)):
    try:
        return service.get_order(db, order_id)
    except service.OrderNotFound:
        raise HTTPException(404, "Orden no encontrada")
