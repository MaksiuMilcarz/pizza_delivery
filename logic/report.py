# logic/report.py
from models import Order, Customer, GenderEnum
from datetime import datetime, timedelta
from sqlalchemy import and_
import csv

def generate_earnings_report(session, month, region=None, customer_id=None, gender=None, min_age=None, max_age=None):
    """
    Generates a monthly earnings report with various filters.
    """
    # Define the start and end dates for the month
    start_date = datetime.strptime(f"{month}-01", "%Y-%m-%d")
    year, mon = month.split('-')
    mon = int(mon)
    if mon == 12:
        end_date = datetime(year=int(year)+1, month=1, day=1)
    else:
        end_date = datetime(year=int(year), month=mon+1, day=1)

    # Base query
    query = session.query(
        Order.id.label('order_id'),
        Customer.name.label('customer_name'),
        Customer.gender.label('gender'),
        Customer.address.label('address'),
        Customer.birthdate.label('birthdate'),
        Order.total_price.label('total_price'),
        Order.order_date.label('order_date')
    ).join(Customer)

    # Filter by month
    query = query.filter(
        Order.order_date >= start_date,
        Order.order_date < end_date
    )

    # Apply additional filters
    if region:
        query = query.filter(Customer.address.like(f"%{region}%"))  # Assuming region is part of the address

    if customer_id:
        query = query.filter(Customer.id == customer_id)

    if gender:
        query = query.filter(Customer.gender == gender)

    if min_age or max_age:
        today = datetime.utcnow().date()
        if min_age:
            max_birthdate = today - timedelta(days=365 * min_age)
            query = query.filter(Customer.birthdate <= max_birthdate)
        if max_age:
            min_birthdate = today - timedelta(days=365 * max_age + 365)
            query = query.filter(Customer.birthdate >= min_birthdate)

    results = query.all()

    # Process results
    report = []
    for record in results:
        age = datetime.utcnow().year - record.birthdate.year - (
            (datetime.utcnow().month, datetime.utcnow().day) < (record.birthdate.month, record.birthdate.day)
        )
        report.append({
            'order_id': record.order_id,
            'customer_name': record.customer_name,
            'gender': record.gender.value,
            'address': record.address,
            'age': age,
            'total_price': float(record.total_price),
            'order_date': record.order_date.strftime('%Y-%m-%d %H:%M:%S')
        })

    return report

def export_report_to_csv(report, filename):
    """
    Exports the earnings report to a CSV file.
    """
    if not report:
        print("No data to export.")
        return

    keys = report[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(report)

    print(f"Report exported to {filename}")
