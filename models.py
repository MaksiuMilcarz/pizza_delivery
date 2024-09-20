"""
File containing all SQLAlchemy ORM models representing our schema.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    UniqueConstraint,
    Table
)
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime

Base = declarative_base()

# Enumerations
class GenderEnum(enum.Enum):
    Male = 'Male'
    Female = 'Female'
    Other = 'Other'

class OrderStatusEnum(enum.Enum):
    Pending = 'Pending'
    Dispatched = 'Dispatched'
    Delivered = 'Delivered'

class DeliveryStatusEnum(enum.Enum):
    Being_Prepared = 'Being Prepared'
    In_Process = 'In Process'
    Out_for_Delivery = 'Out for Delivery'
    Delivered = 'Delivered'
    Cancelled = 'Cancelled'

# Association Table for Pizza and Ingredient (Many-to-Many)
pizza_ingredients_table = Table(
    'pizza_ingredients',  # Ensure this matches the actual table name in the database
    Base.metadata,
    Column('pizza_id', Integer, ForeignKey('pizza.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredient.id'), primary_key=True)
)

# Models
class Pizza(Base):
    __tablename__ = 'pizza'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)

    # Relationships
    ingredients = relationship(
        'Ingredient',
        secondary=pizza_ingredients_table,
        back_populates='pizzas'
    )
    order_pizzas = relationship('Order_Pizzas', back_populates='pizza')


class Ingredient(Base):
    __tablename__ = 'ingredient'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)

    # Relationships
    pizzas = relationship(
        'Pizza',
        secondary=pizza_ingredients_table,
        back_populates='ingredients'
    )


class PizzaIngredients(Base):
    __tablename__ = 'pizza_ingredients'  # Changed to lowercase

    pizza_id = Column(Integer, ForeignKey('pizza.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), primary_key=True)

    # No relationships needed here since it's handled by the association table above
    # If you plan to add additional fields to this association, you can define relationships accordingly


class Drink(Base):
    __tablename__ = 'drink'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order_drinks = relationship('Order_Drinks', back_populates='drink')


class Dessert(Base):
    __tablename__ = 'dessert'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order_desserts = relationship('Order_Desserts', back_populates='dessert')


class Customer(Base):
    __tablename__ = 'customer'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    birthdate = Column(Date, nullable=False)
    phone = Column(String(12), nullable=False)
    address = Column(Text, nullable=False)
    postal_code = Column(String(10), nullable=False)  # Changed to String to accommodate alphanumeric codes
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Increased length for hashed passwords
    total_pizzas_ordered = Column(Integer, default=0)
    birthday_pizza_claimed = Column(Boolean, default=False)

    # Relationships
    orders = relationship('Order', back_populates='customer')
    discount_codes_used = relationship('Discount_Codes_Used', back_populates='customer')


class Order(Base):
    __tablename__ = 'order'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivery_time = Column(DateTime)
    discount_applied = Column(Boolean, default=False)
    birthday_offer_applied = Column(Boolean, default=False)
    discount_code_used = Column(Boolean, default=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.Pending)

    # Relationships
    customer = relationship('Customer', back_populates='orders')
    order_pizzas = relationship('Order_Pizzas', back_populates='order')
    order_drinks = relationship('Order_Drinks', back_populates='order')
    order_desserts = relationship('Order_Desserts', back_populates='order')
    confirmation = relationship('Order_Confirmation', back_populates='order', uselist=False)
    delivery = relationship('Delivery', back_populates='order', uselist=False)
    cancellation = relationship('Order_Cancellation', back_populates='order', uselist=False)
    grouped_orders = relationship('Grouped_Orders', back_populates='order')
    customer_order_status = relationship('Customer_Order_Status', back_populates='order', uselist=False)


class Order_Pizzas(Base):
    __tablename__ = 'order_pizzas'  # Changed to lowercase

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    pizza_id = Column(Integer, ForeignKey('pizza.id'), primary_key=True)
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order = relationship('Order', back_populates='order_pizzas')
    pizza = relationship('Pizza', back_populates='order_pizzas')


class Order_Drinks(Base):
    __tablename__ = 'order_drinks'  # Changed to lowercase

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    drink_id = Column(Integer, ForeignKey('drink.id'), primary_key=True)
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order = relationship('Order', back_populates='order_drinks')
    drink = relationship('Drink', back_populates='order_drinks')


class Order_Desserts(Base):
    __tablename__ = 'order_desserts'  # Changed to lowercase

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    dessert_id = Column(Integer, ForeignKey('dessert.id'), primary_key=True)
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order = relationship('Order', back_populates='order_desserts')
    dessert = relationship('Dessert', back_populates='order_desserts')


class Discount_Codes(Base):
    __tablename__ = 'discount_codes'  # Changed to lowercase

    code = Column(String(20), primary_key=True)
    discount_percentage = Column(DECIMAL(5, 2), nullable=False)

    # Relationships
    used_by = relationship('Discount_Codes_Used', back_populates='code_rel')


class Discount_Codes_Used(Base):
    __tablename__ = 'discount_codes_used'  # Changed to lowercase

    customer_id = Column(Integer, ForeignKey('customer.id'), primary_key=True)
    code = Column(String(20), ForeignKey('discount_codes.code'), primary_key=True)
    is_used = Column(Boolean, default=False)

    # Relationships
    customer = relationship('Customer', back_populates='discount_codes_used')
    code_rel = relationship('Discount_Codes', back_populates='used_by')


class Order_Confirmation(Base):
    __tablename__ = 'order_confirmation'  # Changed to lowercase

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    confirmation_text = Column(Text)
    estimated_delivery_time = Column(DateTime)

    # Relationships
    order = relationship('Order', back_populates='confirmation')


class Delivery_Personnel(Base):
    __tablename__ = 'delivery_personnel'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    phone = Column(String(12), nullable=False)
    postal_code = Column(String(10), nullable=False)  # Changed to String to accommodate alphanumeric codes
    is_available = Column(Boolean, default=True)

    # Relationships
    deliveries = relationship('Delivery', back_populates='delivery_personnel')
    delivery_groupings = relationship('Delivery_Grouping', back_populates='delivery_personnel')


class Delivery(Base):
    __tablename__ = 'delivery'  # Changed to lowercase

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    delivery_personnel_id = Column(Integer, ForeignKey('delivery_personnel.id'), nullable=False)
    status = Column(Enum(DeliveryStatusEnum), default=DeliveryStatusEnum.Being_Prepared, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    estimated_delivery_time = Column(DateTime)
    delivery_time = Column(DateTime)

    # Relationships
    order = relationship('Order', back_populates='delivery')
    delivery_personnel = relationship('Delivery_Personnel', back_populates='deliveries')


class Order_Cancellation(Base):
    __tablename__ = 'order_cancellation'  # Changed to lowercase

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    cancellation_time = Column(DateTime)

    # Relationships
    order = relationship('Order', back_populates='cancellation')


class Delivery_Grouping(Base):
    __tablename__ = 'delivery_grouping'  # Changed to lowercase

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_personnel_id = Column(Integer, ForeignKey('delivery_personnel.id'), nullable=False)
    postal_code = Column(String(10), nullable=False)  # Changed to String to accommodate alphanumeric codes
    group_start_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    delivery_personnel = relationship('Delivery_Personnel', back_populates='delivery_groupings')
    grouped_orders = relationship('Grouped_Orders', back_populates='delivery_grouping')


class Grouped_Orders(Base):
    __tablename__ = 'grouped_orders'  # Changed to lowercase

    group_id = Column(Integer, ForeignKey('delivery_grouping.group_id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)

    # Relationships
    delivery_grouping = relationship('Delivery_Grouping', back_populates='grouped_orders')
    order = relationship('Order')


class Customer_Order_Status(Base):
    __tablename__ = 'customer_order_status'  # Changed to lowercase

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    status_text = Column(String(255))
    estimated_delivery_time = Column(DateTime)

    # Relationships
    order = relationship('Order', back_populates='customer_order_status')
