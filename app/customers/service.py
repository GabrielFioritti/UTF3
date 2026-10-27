"""Interfaz provista ICustomers (la consume el módulo Orders)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.customers.models import Customer
from app.customers.schemas import CustomerIn


class CustomerNotFound(Exception):
    pass


class EmailAlreadyUsed(Exception):
    pass


def create_customer(db: Session, data: CustomerIn) -> Customer:
    exists = db.scalars(select(Customer).where(Customer.email == data.email)).first()
    if exists:
        raise EmailAlreadyUsed(data.email)
    customer = Customer(name=data.name, email=data.email)
    db.add(customer)
    db.flush()
    return customer


def get_customer(db: Session, customer_id: int) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise CustomerNotFound(customer_id)
    return customer
