"""Orders consume las interfaces ICustomers e IProducts.

Todo ocurre dentro de UNA transacción (la sesión `db`): o se valida el
cliente, se descuenta el stock de todos los ítems y se guarda la orden,
o no pasa nada (rollback). Esa es la "A" (atomicidad) de ACID.
"""
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.customers import service as customers
from app.orders.models import Order, OrderItem
from app.orders.schemas import OrderIn
from app.products import service as products


class OrderNotFound(Exception):
    pass


def create_order(db: Session, data: OrderIn) -> Order:
    customers.get_customer(db, data.customer_id)  # ICustomers

    # Unificar ítems repetidos y bloquear productos SIEMPRE en el mismo orden
    # (por id) para que dos órdenes concurrentes no se bloqueen mutuamente.
    quantities: dict[int, int] = defaultdict(int)
    for item in data.items:
        quantities[item.product_id] += item.quantity

    order = Order(customer_id=data.customer_id, status="CONFIRMED", total=Decimal("0"))
    total = Decimal("0")
    for product_id in sorted(quantities):
        qty = quantities[product_id]
        product = products.reserve_stock(db, product_id, qty)  # IProducts
        order.items.append(
            OrderItem(product_id=product_id, quantity=qty, unit_price=product.price)
        )
        total += product.price * qty

    order.total = total
    db.add(order)
    db.flush()
    return order


def get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise OrderNotFound(order_id)
    return order


def list_orders(db: Session) -> list[Order]:
    return list(db.scalars(select(Order).order_by(Order.id)))
