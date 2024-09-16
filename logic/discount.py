# logic/discount.py
from models import Discount_Codes, Discount_Codes_Used
from sqlalchemy.exc import IntegrityError

def add_discount_code(session, code, discount_percentage):
    """
    Adds a new discount code to the system.
    """
    new_code = Discount_Codes(
        code=code,
        discount_percentage=discount_percentage
    )
    session.add(new_code)
    try:
        session.commit()
        print(f"Added Discount Code: {code} with {discount_percentage}% discount.")
    except IntegrityError:
        session.rollback()
        print(f"Discount code {code} already exists.")
    except Exception as e:
        session.rollback()
        print(f"Error adding discount code: {e}")

def track_discount_usage(session, customer_id, code):
    """
    Tracks if a customer has used a specific discount code.
    """
    discount_code = session.query(Discount_Codes).filter_by(code=code).first()
    if not discount_code:
        print("Discount code does not exist.")
        return

    existing_record = session.query(Discount_Codes_Used).filter_by(customer_id=customer_id, code=code).first()
    if not existing_record:
        # Create a new record
        discount_usage = Discount_Codes_Used(
            customer_id=customer_id,
            code=code,
            is_used=False
        )
        session.add(discount_usage)
        try:
            session.commit()
            print(f"Tracked discount code {code} for customer ID {customer_id}.")
        except Exception as e:
            session.rollback()
            print(f"Error tracking discount usage: {e}")
    else:
        print(f"Discount code {code} is already tracked for customer ID {customer_id}.")
