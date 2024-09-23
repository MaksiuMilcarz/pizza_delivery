from decimal import Decimal

from flask import flash
from functionality.order_status_transitions import transition_to_being_delivered, transition_to_being_prepared, transition_to_delivered
from models import Delivery, DiscountCodeUsage, MenuItemCategoryEnum, Order, OrderItem, OrderStatusEnum, MenuItem
from setup.extensions import db
from datetime import datetime, timedelta
from functionality.utils import calculate_final_price
from functionality.delivery import assign_delivery_personnel, calculate_estimated_delivery_interval

def create_order(customer, items, discount_percentage=Decimal('0.00'), discount_code=None):
    total_price = Decimal('0.00')
    new_order = Order(
        customer_id=customer.id,
        order_date=datetime.now(),
        total_price=Decimal('0.00'),  # Will update after adding items
        discount_percentage=discount_percentage,
        status=OrderStatusEnum.Pending,
        is_cancelled=False
    )
    db.session.add(new_order)
    db.session.commit()  # Commit to generate order ID

    total_pizzas_in_order = 0  # To update customer's total_pizzas_ordered

    for item_data in items:
        menu_item = MenuItem.query.get(item_data['menu_item_id'])
        if not menu_item:
            continue  # Skip invalid items

        quantity = item_data['quantity']
        # Calculate final price with profit and VAT
        item_final_price = calculate_final_price(menu_item.base_price)
        item_total_price = item_final_price * quantity
        total_price += item_total_price

        # Count pizzas ordered
        if menu_item.category == MenuItemCategoryEnum.Pizza:
            total_pizzas_in_order += quantity

        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=menu_item.id,
            quantity=quantity,
            price=item_final_price  # Store the final price per unit
        )
        db.session.add(order_item)

    # Update customer's total_pizzas_ordered
    customer.total_pizzas_ordered += total_pizzas_in_order

    # Check if customer is eligible for additional 10% discount
    additional_discount_percentage = Decimal('0.00')
    if customer.total_pizzas_ordered > 10:
        additional_discount_percentage = Decimal('10.00')

    # Calculate total discount percentage
    total_discount_percentage = discount_percentage + additional_discount_percentage

    # Apply total discount to total_price
    if total_discount_percentage > Decimal('0.00'):
        discount_amount = total_price * (total_discount_percentage / Decimal('100.00'))
        total_price -= discount_amount

        # Record the discount code usage if applicable
        if discount_code:
            usage = DiscountCodeUsage.query.filter_by(
                customer_id=customer.id,
                code=discount_code.code
            ).first()
            if not usage:
                usage = DiscountCodeUsage(
                    customer_id=customer.id,
                    code=discount_code.code,
                    is_used=True
                )
                db.session.add(usage)
            else:
                usage.is_used = True  # Update usage status

    # Update order and customer in the database
    new_order.total_price = total_price.quantize(Decimal('0.01'))
    new_order.discount_percentage = total_discount_percentage
    db.session.commit()

    # Assign delivery personnel and create delivery record
    new_delivery = assign_delivery_personnel(new_order)
    if not new_delivery:
        # If no delivery personnel are available, create a delivery record without personnel
        new_delivery = Delivery(
            order_id=new_order.id,
            delivery_personnel_id=None,
            assigned_at=None,
            status=OrderStatusEnum.Waiting_for_Delivery_Personnel,
            estimated_delivery_time=None
        )
        db.session.add(new_delivery)
        db.session.commit()
        
    from app import scheduler
        
    # Transition from Pending to Being Prepared immediately
    scheduler.add_job(
        id=f"transition_to_being_prepared_order_{new_order.id}",
        func=transition_to_being_prepared,
        args=[new_order.id],
        trigger='date',
        run_date=datetime.now()  # Immediate execution
    )

    # Transition from Being Prepared to Being Delivered after 10 minutes
    scheduler.add_job(
        id=f"transition_to_being_delivered_order_{new_order.id}",
        func=transition_to_being_delivered,
        args=[new_order.id],
        trigger='date',
        run_date=datetime.now() + timedelta(minutes=10)
    )
    
    time_to_deliver = calculate_estimated_delivery_interval(new_order, new_delivery)
    scheduler.add_job(
        id=f"transition_to_delivered_order_{new_order.id}",
        func=transition_to_delivered,
        args=[new_order.id],
        trigger='date',
        run_date=datetime.now() + timedelta(minutes=time_to_deliver)
    )

    return new_order