# app.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import GenderEnum
import config
from logic.customer import register_customer, login_customer, update_customer_info
from logic.order import create_order
from logic.discount import add_discount_code, track_discount_usage
from logic.report import generate_earnings_report, export_report_to_csv
from datetime import datetime

# Database setup
DATABASE_URL = f'mysql+pymysql://{config.DATABASE_USERNAME}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}'

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# Example Usage

# 1. Register a new customer
new_customer = register_customer(
    session,
    name='Jane Smith',
    gender=GenderEnum.Female,
    birthdate=datetime.strptime('1990-08-25', '%Y-%m-%d').date(),
    phone='555-6789',
    address='Sorbonnelaan 6229HD, Maastricht',
    email='jane.smith@example.com',
    password='passward123'
)

# 2. Login as the new customer
logged_in_customer = login_customer(session, 'jane.smith@example.com', 'anothersecurepassword')

# 3. Add a new discount code
add_discount_code(session, code='FREEDRINK', discount_percentage=5.00)

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

# Close the session when done
session.close()
