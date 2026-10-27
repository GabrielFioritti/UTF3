"""Interfaz provista IProducts (la consume el módulo Orders)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.products.models import Product
from app.products.schemas import ProductIn


class ProductNotFound(Exception):
    pass


class InsufficientStock(Exception):
    pass


def create_product(db: Session, data: ProductIn) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    db.flush()
    return product


def list_products(db: Session) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.id)))


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise ProductNotFound(product_id)
    return product


def reserve_stock(db: Session, product_id: int, quantity: int) -> Product:
    """Descuenta stock dentro de la transacción del llamador.

    SELECT ... FOR UPDATE bloquea la fila: otra transacción que quiera el
    mismo producto espera hasta que ésta haga commit o rollback.
    """
    product = db.scalars(
        select(Product).where(Product.id == product_id).with_for_update()
    ).one_or_none()
    if product is None:
        raise ProductNotFound(product_id)
    if product.stock < quantity:
        raise InsufficientStock(product_id)
    product.stock -= quantity
    return product
