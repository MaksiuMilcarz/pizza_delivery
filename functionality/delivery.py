# functionality/delivery.py

from models import DeliveryPersonnel, Delivery, MenuItemCategoryEnum, OrderStatusEnum
from setup.extensions import db
from datetime import datetime, timedelta

def assign_delivery_personnel(order):
    customer_postal_code = order.customer.postal_code

    # Get current time
    now = datetime.now()

    # Try to find delivery personnel assigned to this postal code with availability
    delivery_personnel = DeliveryPersonnel.query.filter_by(
        postal_code=customer_postal_code,
        is_available=True
    ).first()

    if not delivery_personnel:
        # If none, find any available delivery personnel without an assigned postal code
        delivery_personnel = DeliveryPersonnel.query.filter_by(
            is_available=True,
            postal_code=None
        ).first()

    if delivery_personnel:
        # Assign them to this postal code if they weren't already
        if delivery_personnel.postal_code != customer_postal_code:
            delivery_personnel.postal_code = customer_postal_code

        # Update last delivery time
        delivery_personnel.last_delivery_time = now

        db.session.commit()

        # Create or update Delivery record
        delivery = Delivery.query.filter_by(order_id=order.id).first()
        if not delivery:
            # Create new delivery
            delivery = Delivery(
                order_id=order.id,
                delivery_personnel_id=delivery_personnel.id,
                assigned_at=now,
                status=OrderStatusEnum.Being_Prepared,
                estimated_delivery_time=calculate_estimated_delivery_time(order, delivery_personnel)
            )
            db.session.add(delivery)
        else:
            # Update existing delivery
            delivery.delivery_personnel_id = delivery_personnel.id
            delivery.assigned_at = now
            delivery.status = OrderStatusEnum.Being_Prepared
            delivery.estimated_delivery_time = calculate_estimated_delivery_time(order, delivery_personnel)

        db.session.commit()

        return delivery
    else:
        # No delivery personnel available; order will wait
        return None
    
"""
def update_pending_deliveries():
    from models import Delivery, DeliveryPersonnel, OrderStatusEnum
    from datetime import datetime, timedelta
    from setup.extensions import db

    now = datetime.now()

    # Find deliveries waiting for personnel
    pending_deliveries = Delivery.query.filter_by(
        delivery_personnel_id=None,
        status=OrderStatusEnum.Waiting_for_Delivery_Personnel
    ).all()

    for delivery in pending_deliveries:
        order = delivery.order
        assigned_delivery_personnel = assign_delivery_personnel(order)
        if assigned_delivery_personnel:
            # Update delivery record
            delivery.delivery_personnel_id = assigned_delivery_personnel.delivery_personnel_id
            delivery.assigned_at = assigned_delivery_personnel.assigned_at
            delivery.status = assigned_delivery_personnel.status
            delivery.estimated_delivery_time = assigned_delivery_personnel.estimated_delivery_time
            db.session.commit()
"""
  
def calculate_estimated_delivery_time(order, delivery_personnel):
    from datetime import datetime, timedelta

    # Base preparation time
    preparation_time = timedelta(minutes=5)  # Base time for order preparation

    # Additional time per item
    additional_time_per_item = timedelta(minutes=1)

    # Calculate total additional time based on number of pizzas and desserts
    total_additional_time = timedelta()
    for order_item in order.order_items:
        if order_item.menu_item.category in [MenuItemCategoryEnum.Pizza, MenuItemCategoryEnum.Dessert]:
            total_additional_time += additional_time_per_item * order_item.quantity

    # Estimate delivery time based on postal code (simplified)
    # For example, add 1 minute per unit difference in postal codes
    # Assuming postal codes are numeric strings
    try:
        restaurant_postal_code = 6211  # Example postal code of the restaurant
        customer_postal_code = int(order.customer.postal_code)
        postal_code_difference = abs(customer_postal_code - restaurant_postal_code)//2
        delivery_distance_time = timedelta(minutes=postal_code_difference)
    except ValueError:
        # Default delivery time if postal codes are non-numeric
        delivery_distance_time = timedelta(minutes=10)

    # Additional time if delivery person has other orders
    other_orders = Delivery.query.filter(
        Delivery.delivery_personnel_id == delivery_personnel.id,
        Delivery.status == OrderStatusEnum.Being_Prepared,
        Delivery.order_id != order.id
    ).count()
    additional_delivery_time = timedelta(minutes=5 * other_orders)

    # Total estimated delivery time
    total_estimated_time = datetime.now() + preparation_time + total_additional_time + delivery_distance_time + additional_delivery_time

    return total_estimated_time

def calculate_estimated_delivery_interval(order, delivery_personnel):
    # Base preparation time
    preparation_time = 5 

    # Additional time per item
    additional_time_per_item = 1

    # Calculate total additional time based on number of pizzas and desserts
    total_additional_time = 0
    for order_item in order.order_items:
        if order_item.menu_item.category in [MenuItemCategoryEnum.Pizza, MenuItemCategoryEnum.Dessert]:
            total_additional_time += additional_time_per_item * order_item.quantity

    # Estimate delivery time based on postal code (simplified)
    # For example, add 1 minute per unit difference in postal codes
    # Assuming postal codes are numeric strings
    try:
        restaurant_postal_code = 6211  # Example postal code of the restaurant
        customer_postal_code = int(order.customer.postal_code)
        postal_code_difference = abs(customer_postal_code - restaurant_postal_code)//2
        delivery_distance_time = postal_code_difference
    except ValueError:
        # Default delivery time if postal codes are non-numeric
        delivery_distance_time = 10

    # Additional time if delivery person has other orders
    other_orders = Delivery.query.filter(
        Delivery.delivery_personnel_id == delivery_personnel.id,
        Delivery.status == OrderStatusEnum.Being_Prepared,
        Delivery.order_id != order.id
    ).count()
    additional_delivery_time = 5 * other_orders

    # Total estimated delivery time
    total_estimated_interval = preparation_time + total_additional_time + delivery_distance_time + additional_delivery_time

    return total_estimated_interval

def complete_delivery(delivery_id):
    delivery = Delivery.query.get(delivery_id)
    if not delivery:
        raise ValueError("Delivery not found.")
    
    if delivery.status == OrderStatusEnum.Delivered:
        raise ValueError("Delivery is already completed.")
    
    # Update delivery status to Delivered
    delivery.status = OrderStatusEnum.Delivered
    delivery.delivery_time = datetime.now()
    
    # Update the associated order's status to Delivered
    order = delivery.order
    if order:
        order.status = OrderStatusEnum.Delivered
        db.session.commit()
    else:
        raise ValueError("Associated order not found.")
    
    # Check if the delivery personnel has other active deliveries
    delivery_personnel = delivery.delivery_personnel
    if delivery_personnel:
        # Query for other active deliveries assigned to this personnel
        active_deliveries = Delivery.query.filter(
            Delivery.delivery_personnel_id == delivery_personnel.id,
            Delivery.status.in_([OrderStatusEnum.Being_Prepared, OrderStatusEnum.Being_Delivered])
        ).count()
        
        if active_deliveries == 0:
            # No other active deliveries; mark as available
            delivery_personnel.is_available = True
            delivery_personnel.postal_code = None  # Unassign postal code if necessary
            delivery_personnel.last_delivery_time = datetime.now()
            db.session.commit()
        else:
            # The delivery personnel has other active deliveries; do not mark as available
            pass  # No action needed
    else:
        raise ValueError("Delivery personnel not found.")
        
    db.session.commit()