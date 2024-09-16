# logic/customer.py
from sqlalchemy.exc import IntegrityError, NoResultFound
from models import Customer, GenderEnum
from utils.security import hash_password, verify_password
from datetime import datetime

def register_customer(session, name, gender, birthdate, phone, address,postal_code, email, password):
    """
    Registers a new customer.
    """
    hashed_pwd = hash_password(password)
    new_customer = Customer(
        name=name,
        gender=gender,
        birthdate=birthdate,
        phone=phone,
        address=address,
        postal_code=postal_code,
        email=email,
        password=hashed_pwd
    )
    session.add(new_customer)
    try:
        session.commit()
        print(f"Registered Customer ID: {new_customer.id}")
        return new_customer
    except IntegrityError:
        session.rollback()
        print("Email already exists.")
        return None
    except Exception as e:
        session.rollback()
        print(f"Error registering customer: {e}")
        return None

def login_customer(session, email, password):
    """
    Authenticates a customer.
    """
    try:
        customer = session.query(Customer).filter_by(email=email).one()
        if verify_password(customer.password, password):
            print(f"Logged in as: {customer.name}")
            return customer
        else:
            print("Invalid password.")
            return None
    except NoResultFound:
        print("Customer not found.")
        return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def update_customer_info(session, customer_id, **kwargs):
    """
    Updates customer information.
    """
    try:
        customer = session.query(Customer).filter_by(id=customer_id).one()
        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        session.commit()
        print("Customer information updated.")
        return customer
    except NoResultFound:
        print("Customer not found.")
        return None
    except Exception as e:
        session.rollback()
        print(f"Error updating customer information: {e}")
        return None
