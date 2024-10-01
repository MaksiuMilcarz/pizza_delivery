from models import Order, OrderStatusEnum, DeliveryPersonnel, Delivery
from setup.extensions import db
from datetime import datetime

def transition_to_being_prepared(order_id):
    from app import app as current_app
    with current_app.app_context():
        order = Order.query.get(order_id)
        if order and order.status == OrderStatusEnum.Pending:
            order.status = OrderStatusEnum.Being_Prepared
            db.session.commit()
            
            # Optionally, notify the kitchen or perform other actions here
            current_app.logger.info(f"Order {order_id} status changed to Being Prepared.")
            print(f"Order {order_id} status changed to Being Prepared.")

def transition_to_being_delivered(order_id):
    from app import app as current_app
    with current_app.app_context():
        order = Order.query.get(order_id)
        if order and order.status == OrderStatusEnum.Being_Prepared:
            # Update order status
            order.status = OrderStatusEnum.Being_Delivered
            
            # Update delivery status
            delivery = order.delivery
            if delivery:
                delivery.status = OrderStatusEnum.Being_Delivered
            else:
                current_app.logger.error(f"No delivery found for Order ID {order_id}")
                return
            
            # Mark delivery personnel as unavailable
            delivery_personnel = delivery.delivery_personnel
            if delivery_personnel:
                delivery_personnel.is_available = False
            else:
                current_app.logger.error(f"No delivery personnel assigned for Delivery ID {delivery.id}")
                return
            
            # Commit all changes
            db.session.commit()
            
            current_app.logger.info(f"Order {order_id} status changed to Being Delivered and Delivery Personnel {delivery_personnel.name} marked as unavailable.")
            print(f"Order {order_id} status changed to Being Delivered and Delivery Personnel {delivery_personnel.name} marked as unavailable.")
            
def transition_to_delivered(order_id):
    from app import app as current_app
    with current_app.app_context():
        order = Order.query.get(order_id)
        if order and order.status == OrderStatusEnum.Being_Delivered:
            # Update order status to Delivered
            order.status = OrderStatusEnum.Delivered

            # Update the delivery status to Delivered
            delivery = order.delivery
            if delivery:
                delivery.status = OrderStatusEnum.Delivered
                delivery.delivery_time = datetime.now()
            else:
                current_app.logger.error(f"Delivery record not found for Order {order_id}.")
                print(f"Delivery record not found for Order {order_id}.")

            db.session.commit()
            
            # Check if the delivery personnel has other active deliveries
            delivery_personnel = delivery.delivery_personnel if delivery else None
            if delivery_personnel:
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
                current_app.logger.error(f"Delivery personnel not found for Order {order_id}.")
                print(f"Delivery personnel not found for Order {order_id}.")

            current_app.logger.info(f"Order {order_id} status changed to Delivered.")
            print(f"Order {order_id} status changed to Delivered.")