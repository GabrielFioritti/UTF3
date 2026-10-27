from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.products import service
from app.products.schemas import ProductIn, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductOut, status_code=201)
def create(data: ProductIn, db: Session = Depends(get_db)):
    product = service.create_product(db, data)
    db.commit()
    return product


@router.get("", response_model=list[ProductOut])
def list_all(db: Session = Depends(get_db)):
    return service.list_products(db)


@router.get("/{product_id}", response_model=ProductOut)
def get_one(product_id: int, db: Session = Depends(get_db)):
    try:
        return service.get_product(db, product_id)
    except service.ProductNotFound:
        raise HTTPException(404, "Producto no encontrado")
