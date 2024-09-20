"""
The main entry point for the application.
"""
# app.py
import logging
from flask import Flask, render_template, request, redirect, url_for, session as flask_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, GenderEnum
import config
from logic.customer import register_customer, login_customer, update_customer_info
from logic.order import create_order
from logic.discount import add_discount_code, track_discount_usage
from logic.report import generate_earnings_report, export_report_to_csv
from datetime import datetime
from models import (
    Base,
    GenderEnum,
    OrderStatusEnum,
    DeliveryStatusEnum,
    Pizza,
    Ingredient,
    pizza_ingredients_table,
    Drink,
    Dessert,
    Customer,
    Order,
    Order_Pizzas,
    Order_Drinks,
    Order_Desserts,
    Discount_Codes,
    Discount_Codes_Used,
    Order_Confirmation,
    Delivery_Personnel,
    Delivery,
    Order_Cancellation,
    Delivery_Grouping,
    Grouped_Orders,
    Customer_Order_Status
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Database setup
    DATABASE_URL = f'mysql+pymysql://{config.DATABASE_USERNAME}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}'
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL, echo=True)
        logger.info("Database engine created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        return
    
    try:
        # Create a configured "Session" class
        Session = sessionmaker(bind=engine)
        logger.info("Sessionmaker configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure sessionmaker: {e}")
        return
    
    try:
        # Create a session
        session = Session()
        logger.info("Database session created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        return

    try:
        # 1. Register a new customer
        new_customer = register_customer(
            session,
            name='Rosa Melano',
            gender=GenderEnum.Female,
            birthdate=datetime.strptime('1990-08-25', '%Y-%m-%d').date(),
            phone='555-6789',
            address='Sorbonnelaan, Maastricht',
            postal_code='6229HD',
            email='jane.smith@example.com',
            password='passward123'
        )
        logger.info(f"Registered new customer: {new_customer.email}")
    except Exception as e:
        logger.error(f"Error registering customer: {e}")
    
    try:
        # 2. Login as the new customer
        logged_in_customer = login_customer(session, 'jane.smith@example.com', 'anothersecurepassword')
        if logged_in_customer:
            logger.info(f"Customer logged in successfully: {logged_in_customer.email}")
        else:
            logger.warning("Login failed: Invalid credentials.")
    except Exception as e:
        logger.error(f"Error logging in customer: {e}")
        logged_in_customer = None
    
    try:
        # 3. Add a new discount code
        add_discount_code(session, code='FREEDRINK', discount_percentage=5.00)
        logger.info("Added new discount code: FREEDRINK")
    except Exception as e:
        logger.error(f"Error adding discount code: {e}")
    
    try:
        # 4. Create an order
        if logged_in_customer:
            order_details = create_order(
                session,
                customer=logged_in_customer,
                pizzas=[{'pizza_id': 2, 'quantity': 3}],  # Replace with valid pizza IDs
                drinks=[{'drink_id': 2, 'quantity': 2}],  # Replace with valid drink IDs
                desserts=[{'dessert_id': 1, 'quantity': 1}],  # Replace with valid dessert IDs
                discount_code='SAVE10'  # Replace with a valid discount code
            )
            logger.info(f"Order created successfully: Order ID {order_details.id}")
        else:
            logger.warning("Order creation skipped: Customer not logged in.")
    except Exception as e:
        logger.error(f"Error creating order: {e}")
    
    try:
        # 5. Generate and export an earnings report
        report = generate_earnings_report(
            session,
            month='2024-08',
            region='12345',
            gender=GenderEnum.Female,
            min_age=25,
            max_age=35
        )
        export_report_to_csv(report, 'earnings_report_august_2024.csv')
        logger.info("Earnings report generated and exported successfully.")
    except Exception as e:
        logger.error(f"Error generating or exporting earnings report: {e}")
    
    try:
        # Track discount usage (if applicable)
        track_discount_usage(session, 'FREEDRINK')
        logger.info("Tracked discount usage for code: FREEDRINK")
    except Exception as e:
        logger.error(f"Error tracking discount usage: {e}")
    
    try:
        # Commit all changes to the database
        session.commit()
        logger.info("Database session committed successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error committing session: {e}")
    finally:
        # Close the session when done
        session.close()
        logger.info("Database session closed.")

if __name__ == "__main__":
    main()
