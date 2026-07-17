from datetime import date
from flask_sqlalchemy import SQLAlchemy  # type: ignore[import-not-found]
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, ForeignKey, String, Date, Integer
from typing import List

# Create a base class for the models
class Base(DeclarativeBase):
    pass

# Instantiate the SQLAlchemy database object
db = SQLAlchemy(model_class=Base)

# Association table for the many-to-many relationship 
# between ServiceTicket and Mechanic
ticket_mechanic = Table(
    'ticket_mechanic',
    Base.metadata,
    Column('ticket_id', ForeignKey('service_tickets.id'), primary_key=True),
    Column('mechanic_id', ForeignKey('mechanics.id'), primary_key=True)
)

class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    specialty: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationship attribute: allows us to treat mechanics.tickets like a list
    tickets: Mapped[List['ServiceTicket']] = relationship(
        secondary=ticket_mechanic, back_populates='mechanics'
    )

class ServiceTicket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationship attribute: allows us to treat ticket.mechanics like a list
    # (Used for appending/removing mechanics in your routes)
    mechanics: Mapped[List['Mechanic']] = relationship(
        secondary=ticket_mechanic, back_populates='tickets'
    )
