# logic/order.py
from sqlalchemy.exc import NoResultFound
from models import (
    Order,
    Order_Pizzas,
    Order_Drinks,
    Order_Desserts,
    OrderStatusEnum,
    DeliveryStatusEnum,
    Discount_Codes_Used,
    Discount_Codes,
    Order_Confirmation,
    Delivery,
    Grouped_Orders,
    Delivery_Grouping,
    Customer_Order_Status
)
from utils.security import hash_password, verify_password
from datetime import datetime, timedelta
from utils.email import send_order_confirmation_email

def create_order(session, customer, pizzas, drinks=None, desserts=None, discount_code=None):
    """
    Creates a new order for a customer.
    """
    if not pizzas or len(pizzas) == 0:
        print("Each order must contain at least one pizza.")
        return None

    total_price = 0.0
    order_pizzas = []
    for item in pizzas:
        try:
            pizza = session.query(Order_Pizzas.pizza).filter_by(id=item['pizza_id']).one()
        except NoResultFound:
            print(f"Pizza ID {item['pizza_id']} not found.")
            continue
        subtotal = float(pizza.base_price) * item['quantity']
        total_price += subtotal
        order_pizzas.append(Order_Pizzas(pizza_id=pizza.id, quantity=item['quantity'], price=pizza.base_price))

    order_drinks = []
    if drinks:
        for item in drinks:
            try:
                drink = session.query(Order_Drinks.drink).filter_by(id=item['drink_id']).one()
            except NoResultFound:
                print(f"Drink ID {item['drink_id']} not found.")
                continue
            subtotal = float(drink.base_price) * item['quantity']
            total_price += subtotal
            order_drinks.append(Order_Drinks(drink_id=drink.id, quantity=item['quantity'], price=drink.base_price))

    order_desserts = []
    if desserts:
        for item in desserts:
            try:
                dessert = session.query(Order_Desserts.dessert).filter_by(id=item['dessert_id']).one()
            except NoResultFound:
                print(f"Dessert ID {item['dessert_id']} not found.")
                continue
            subtotal = float(dessert.base_price) * item['quantity']
            total_price += subtotal
            order_desserts.append(Order_Desserts(dessert_id=dessert.id, quantity=item['quantity'], price=dessert.base_price))

    # Apply discounts
    discount = 0.0

    # 10% discount if customer has ordered 10 or more pizzas
    if customer.total_pizzas_ordered >= 10:
        discount += 0.10
        print("Applied 10% discount for ordering 10 or more pizzas.")

    # Apply discount code
    if discount_code:
        discount_record = session.query(Discount_Codes_Used).join(Discount_Codes).filter(
            Discount_Codes.code == discount_code,
            Discount_Codes_Used.customer_id == customer.id,
            Discount_Codes_Used.is_used == False
        ).first()

        if discount_record:
            discount += float(discount_record.code_rel.discount_percentage) / 100
            discount_record.is_used = True
            print(f"Applied {discount_record.code_rel.discount_percentage}% discount using code {discount_code}.")
        else:
            print("Invalid or already used discount code.")

    total_price_after_discount = total_price * (1 - discount)

    # Create the order
    new_order = Order(
        customer_id=customer.id,
        total_price=total_price_after_discount,
        order_date=datetime.utcnow(),
        status=OrderStatusEnum.Pending,
        discount_applied=bool(discount),
        discount_code_used=bool(discount_code)
    )

    session.add(new_order)
    try:
        session.commit()
        print(f"Created Order ID: {new_order.id}")
    except Exception as e:
        session.rollback()
        print(f"Error creating order: {e}")
        return None

    # Associate pizzas, drinks, and desserts with the order
    for op in order_pizzas:
        op.order_id = new_order.id
        session.add(op)

    for od in order_drinks:
        od.order_id = new_order.id
        session.add(od)

    for od in order_desserts:
        od.order_id = new_order.id
        session.add(od)

    # Increment total_pizzas_ordered
    total_pizzas = sum([item['quantity'] for item in pizzas])
    customer.total_pizzas_ordered += total_pizzas
    session.add(customer)

    # Handle birthday offer
    today = datetime.utcnow().date()
    if (customer.birthdate.month == today.month and customer.birthdate.day == today.day and not customer.birthday_pizza_claimed):
        # Assuming pizza_id=1 and drink_id=1 are free
        free_pizza = Order_Pizzas(order_id=new_order.id, pizza_id=1, quantity=1, price=0.00)
        free_drink = Order_Drinks(order_id=new_order.id, drink_id=1, quantity=1, price=0.00)
        session.add(free_pizza)
        session.add(free_drink)
        customer.birthday_pizza_claimed = True
        print("Applied birthday offer: Free pizza and drink.")

    # Generate order confirmation
    estimated_delivery_time = datetime.utcnow() + timedelta(minutes=30)
    confirmation_text = f"Thank you for your order, {customer.name}! Your order #{new_order.id} will be delivered by {estimated_delivery_time.strftime('%H:%M')}."

    order_confirmation = Order_Confirmation(
        order_id=new_order.id,
        confirmation_text=confirmation_text,
        estimated_delivery_time=estimated_delivery_time
    )
    session.add(order_confirmation)

    # Optionally, send confirmation via email
    send_order_confirmation_email(customer.email, confirmation_text)

    try:
        session.commit()
        print(f"Order Confirmation created for Order ID: {new_order.id}")
    except Exception as e:
        session.rollback()
        print(f"Error creating order confirmation: {e}")
        return None

    return {
        'order_id': new_order.id,
        'confirmation_text': confirmation_text,
        'estimated_delivery_time': estimated_delivery_time
    }
