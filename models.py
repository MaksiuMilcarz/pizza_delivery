from decimal import Decimal
from flask_login import UserMixin
from sqlalchemy import Column, DateTime, Integer, String, DECIMAL, Boolean, Date, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from setup.extensions import db
import enum
from datetime import datetime

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
    Waiting_for_Delivery_Personnel = 'Waiting for Delivery Personnel'
    Being_Delivered = 'Being Delivered'
    Delivered = 'Delivered'
    Cancelled = 'Cancelled'

## MenuItem
class MenuItem(db.Model):
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
        backref=db.backref('menu_items', lazy='dynamic')
    )
    order_items = relationship('OrderItem', back_populates='menu_item')

## Ingredient
class Ingredient(db.Model):
    __tablename__ = 'Ingredient'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)

## MenuItemIngredient (Association Table)
class MenuItemIngredient(db.Model):
    __tablename__ = 'MenuItemIngredient'

    menu_item_id = db.Column(db.Integer, db.ForeignKey('MenuItem.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('Ingredient.id'), primary_key=True)

## Customer
class Customer(UserMixin, db.Model):  # Inherit from UserMixin
    __tablename__ = 'Customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    birthdate = Column(Date, nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(Text, nullable=False)
    postal_code = Column(String(10), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed passwords
    total_pizzas_ordered = Column(Integer, default=0)
    birthday_pizza_claimed = Column(Boolean, default=False)

    # Relationships
    orders = relationship('Order', back_populates='customer')
    discount_code_usages = relationship('DiscountCodeUsage', back_populates='customer')
    
    def get_id(self):
        return str(self.id)

## Order
class Order(db.Model):
    __tablename__ = 'Order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('Customer.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.now, nullable=False)
    delivery_time = Column(DateTime)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    discount_percentage = Column(DECIMAL(5, 2), default=Decimal('0.00'))
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.Pending)
    is_cancelled = Column(Boolean, default=False)
    cancellation_time = Column(DateTime)

    # Relationships
    customer = relationship('Customer', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    delivery = relationship('Delivery', back_populates='order', uselist=False)
    status_history = relationship('OrderStatusHistory', back_populates='order')

## OrderItem
class OrderItem(db.Model):
    __tablename__ = 'OrderItem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Order.id'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('MenuItem.id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order = relationship('Order', back_populates='order_items')
    menu_item = relationship('MenuItem')

## DiscountCode
class DiscountCode(db.Model):
    __tablename__ = 'DiscountCode'

    code = Column(String(20), primary_key=True)
    discount_percentage = Column(DECIMAL(5, 2), nullable=False)

    # Relationships
    usages = relationship('DiscountCodeUsage', back_populates='discount_code')

## DiscountCodeUsage
class DiscountCodeUsage(db.Model):
    __tablename__ = 'DiscountCodeUsage'

    customer_id = Column(Integer, ForeignKey('Customer.id'), primary_key=True)
    code = Column(String(20), ForeignKey('DiscountCode.code'), primary_key=True)
    is_used = Column(Boolean, default=False)

    # Relationships
    customer = relationship('Customer', back_populates='discount_code_usages')
    discount_code = relationship('DiscountCode', back_populates='usages')

## DeliveryPersonnel
class DeliveryPersonnel(db.Model):
    __tablename__ = 'DeliveryPersonnel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    postal_code = Column(String(10), nullable=True)  # Changed nullable to True
    is_available = Column(Boolean, default=True)
    last_delivery_time = Column(DateTime)

    # Relationships
    deliveries = relationship('Delivery', back_populates='delivery_personnel')

## Delivery
class Delivery(db.Model):
    __tablename__ = 'Delivery'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Order.id'), nullable=False, unique=True)
    delivery_personnel_id = Column(Integer, ForeignKey('DeliveryPersonnel.id'), nullable=True)
    assigned_at = Column(DateTime, default=datetime.now)
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.Being_Prepared)
    estimated_delivery_time = Column(DateTime)
    delivery_time = Column(DateTime)

    # Relationships
    order = relationship('Order', back_populates='delivery')
    delivery_personnel = relationship('DeliveryPersonnel', back_populates='deliveries')

## OrderStatusHistory (Optional)
class OrderStatusHistory(db.Model):
    __tablename__ = 'OrderStatusHistory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Order.id'), nullable=False)
    status = Column(Enum(OrderStatusEnum), nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    order = relationship('Order', back_populates='status_history')