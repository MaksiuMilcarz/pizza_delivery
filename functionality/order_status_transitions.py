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
            order.status = OrderStatusEnum.Being_Delivered
            db.session.commit()
            
            # Optionally, notify the delivery personnel or perform other actions here
            current_app.logger.info(f"Order {order_id} status changed to Being Delivered.")
            print(f"Order {order_id} status changed to Being Delivered.")
            
def transition_to_delivered(order_id):
    from app import app as current_app
    with current_app.app_context():
        order = Order.query.get(order_id)
        if order and order.status == OrderStatusEnum.Being_Delivered:
            order.status = OrderStatusEnum.Delivered
            db.session.commit()
            
            # Check if the delivery personnel has other active deliveries
            delivery_personnel = order.delivery.delivery_personnel
            if delivery_personnel:
                active_deliveries = Delivery.query.filter(
                    Delivery.delivery_personnel_id == delivery_personnel.id,
                    Delivery.status.in_([OrderStatusEnum.Being_Prepared, OrderStatusEnum.Being_Delivered])
                ).count()
                
                if active_deliveries <= 1:
                    # Only this delivery is active; mark as available
                    delivery_personnel.is_available = True
                    delivery_personnel.postal_code = None  # Unassign postal code if necessary
                    delivery_personnel.last_delivery_time = datetime.now()
                else:
                    # The delivery personnel has other active deliveries; do not mark as available
                    pass  # No action needed
                
                db.session.commit()
            
            current_app.logger.info(f"Order {order_id} status changed to Delivered and Delivery Personnel {delivery_personnel.name} is now available.")
            print(f"Order {order_id} status changed to Delivered and Delivery Personnel {delivery_personnel.name} is now available.")