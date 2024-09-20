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
    func
)
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime

Base = declarative_base()

# Enumerations
class MenuItemCategoryEnum(enum.Enum):
    Pizza = 'Pizza'
    Drink = 'Drink'
    Dessert = 'Dessert'

class GenderEnum(enum.Enum):
    Male = 'Male'
    Female = 'Female'
    Other = 'Other'

class OrderStatusEnum(enum.Enum):
    Pending = 'Pending'
    Being_Prepared = 'Being Prepared'
    In_Process = 'In Process'
    Out_for_Delivery = 'Out for Delivery'
    Delivered = 'Delivered'
    Cancelled = 'Cancelled'

# Models

## MenuItem
class MenuItem(Base):
    __tablename__ = 'MenuItem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    category = Column(Enum(MenuItemCategoryEnum), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)

    # Relationships
    ingredients = relationship(
        'Ingredient',
        secondary='MenuItemIngredient',
        back_populates='menu_items'
    )
    order_items = relationship('OrderItem', back_populates='menu_item')

## Ingredient
class Ingredient(Base):
    __tablename__ = 'Ingredient'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)

    # Relationships
    menu_items = relationship(
        'MenuItem',
        secondary='MenuItemIngredient',
        back_populates='ingredients'
    )

## MenuItemIngredient (Association Table)
class MenuItemIngredient(Base):
    __tablename__ = 'MenuItemIngredient'

    menu_item_id = Column(Integer, ForeignKey('MenuItem.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('Ingredient.id'), primary_key=True)

    # Relationships (optional, since we're using secondary in MenuItem and Ingredient)
    menu_item = relationship('MenuItem', back_populates='ingredients')
    ingredient = relationship('Ingredient', back_populates='menu_items')

## Customer
class Customer(Base):
    __tablename__ = 'Customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    birthdate = Column(Date, nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(Text, nullable=False)
    postal_code = Column(String(10), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Use hashed passwords
    total_pizzas_ordered = Column(Integer, default=0)
    birthday_pizza_claimed = Column(Boolean, default=False)

    # Relationships
    orders = relationship('Order', back_populates='customer')
    discount_code_usages = relationship('DiscountCodeUsage', back_populates='customer')

## Order
class Order(Base):
    __tablename__ = 'Order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('Customer.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivery_time = Column(DateTime)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    discount_percentage = Column(DECIMAL(5, 2), default=0)
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.Pending)
    is_cancelled = Column(Boolean, default=False)
    cancellation_time = Column(DateTime)

    # Relationships
    customer = relationship('Customer', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')
    delivery = relationship('Delivery', back_populates='order', uselist=False)
    status_history = relationship('OrderStatusHistory', back_populates='order')

## OrderItem
class OrderItem(Base):
    __tablename__ = 'OrderItem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Order.id'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('MenuItem.id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order = relationship('Order', back_populates='order_items')
    menu_item = relationship('MenuItem', back_populates='order_items')

## DiscountCode
class DiscountCode(Base):
    __tablename__ = 'DiscountCode'

    code = Column(String(20), primary_key=True)
    discount_percentage = Column(DECIMAL(5, 2), nullable=False)

    # Relationships
    usages = relationship('DiscountCodeUsage', back_populates='discount_code')

## DiscountCodeUsage
class DiscountCodeUsage(Base):
    __tablename__ = 'DiscountCodeUsage'

    customer_id = Column(Integer, ForeignKey('Customer.id'), primary_key=True)
    code = Column(String(20), ForeignKey('DiscountCode.code'), primary_key=True)
    is_used = Column(Boolean, default=False)

    # Relationships
    customer = relationship('Customer', back_populates='discount_code_usages')
    discount_code = relationship('DiscountCode', back_populates='usages')

## DeliveryPersonnel
class DeliveryPersonnel(Base):
    __tablename__ = 'DeliveryPersonnel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    postal_code = Column(String(10), nullable=False)
    is_available = Column(Boolean, default=True)
    last_delivery_time = Column(DateTime)

    # Relationships
    deliveries = relationship('Delivery', back_populates='delivery_personnel')

## Delivery
class Delivery(Base):
    __tablename__ = 'Delivery'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Order.id'), nullable=False, unique=True)
    delivery_personnel_id = Column(Integer, ForeignKey('DeliveryPersonnel.id'), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.Being_Prepared)
    estimated_delivery_time = Column(DateTime)
    delivery_time = Column(DateTime)

    # Relationships
    order = relationship('Order', back_populates='delivery')
    delivery_personnel = relationship('DeliveryPersonnel', back_populates='deliveries')

## OrderStatusHistory (Optional)
class OrderStatusHistory(Base):
    __tablename__ = 'OrderStatusHistory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Order.id'), nullable=False)
    status = Column(Enum(OrderStatusEnum), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    order = relationship('Order', back_populates='status_history')