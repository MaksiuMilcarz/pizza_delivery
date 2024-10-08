from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functionality.customer import create_customer
from functionality.delivery import complete_delivery
from functionality.order import create_order
from functionality.order import cancel_order
from functionality.utils import calculate_final_price
from models import Customer, Delivery, DeliveryPersonnel, DiscountCode, DiscountCodeUsage, MenuItem, Order, OrderItem, OrderStatusEnum
from forms import EarningsReportFilterForm, RegistrationForm, LoginForm, OrderForm, OrderItemForm
from datetime import datetime
from flask import jsonify

def register_routes(app):
    @app.route('/my_orders', methods=['GET'])
    @login_required
    def my_orders():
        from setup.extensions import db 
        # Fetch orders belonging to the current user
        orders = db.session.query(
            Order.id.label('order_id'),
            Order.order_date,
            Order.status,
            DeliveryPersonnel.name.label('delivery_personnel_name'),
            DeliveryPersonnel.phone.label('delivery_personnel_phone')
        ).outerjoin(Order.delivery).outerjoin(DeliveryPersonnel).filter(
            Order.customer_id == current_user.id
        ).all()

        return render_template('my_orders.html', orders=orders)

    @app.route('/earnings_report', methods=['GET', 'POST'])
    @login_required
    def earnings_report():
        from setup.extensions import db
        from datetime import datetime, date, timedelta
        from decimal import Decimal
        # Access control: Only admins can access
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('order'))

        form = EarningsReportFilterForm(request.args)
        filters = []
        if form.validate():
            # Filter by postal code
            if form.postal_code.data:
                filters.append(Customer.postal_code == form.postal_code.data)
            # Filter by gender
            if form.gender.data:
                filters.append(Customer.gender == form.gender.data)
            # Filter by age range
            today = date.today()
            if form.min_age.data is not None:
                try:
                    max_birthdate = date(today.year - form.min_age.data, today.month, today.day)
                    filters.append(Customer.birthdate <= max_birthdate)
                except ValueError as e:
                    flash(f'Invalid minimum age input: {e}', 'danger')
            if form.max_age.data is not None:
                try:
                    min_birthdate = date(today.year - form.max_age.data - 1, today.month, today.day) + timedelta(days=1)
                    filters.append(Customer.birthdate >= min_birthdate)
                except ValueError as e:
                    flash(f'Invalid maximum age input: {e}', 'danger')
        else:
            if request.args:
                flash('Invalid filter inputs.', 'warning')
                # Log form errors for debugging
                app.logger.warning(f"EarningsReportFilterForm validation errors: {form.errors}")

        # Join Orders with Customers
        query = db.session.query(
            Order.id.label('order_id'),
            Order.order_date,
            Order.total_price,
            Customer.name.label('customer_name'),
            Customer.gender,
            Customer.birthdate,
            Customer.postal_code
        ).join(Customer)

        if filters:
            query = query.filter(*filters)

        # Retrieve orders
        orders = query.all()

        # Calculate aggregates
        total_earnings = sum(order.total_price for order in orders) or Decimal('0.00')
        total_orders = len(orders)
        average_order_value = (total_earnings / total_orders) if total_orders > 0 else Decimal('0.00')

        return render_template('earnings_report.html', form=form, orders=orders,
                               total_earnings=total_earnings,
                               total_orders=total_orders,
                               average_order_value=average_order_value,
                               date=date)  # Pass 'date' to the template

    @app.route('/order_management', methods=['GET'])
    @login_required
    def order_management():
        from setup.extensions import db
        # Access control: Only admins can access this page
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))  # Redirect to order page or any other appropriate page

        # Fetch all orders, joined with customer and delivery personnel
        orders = db.session.query(
            Order.id.label('order_id'),
            Order.order_date,
            Customer.name.label('customer_name'),
            Order.status,
            DeliveryPersonnel.name.label('delivery_personnel_name'),
            Customer.postal_code
        ).join(Customer).outerjoin(Order.delivery).outerjoin(DeliveryPersonnel).all()

        return render_template('order_management.html', orders=orders)
    
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if email already exists
            existing_user = Customer.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already exists. Please log in.', 'danger')
                return redirect(url_for('login'))

            hashed_password = generate_password_hash(form.password.data)  # Updated method
            
            create_customer(form, hashed_password)
               
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form) 


    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')
    


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            # Query the customer
            customer = Customer.query.filter_by(email=form.email.data).first()
            if customer and check_password_hash(customer.password, form.password.data):
                login_user(customer)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'danger')
        return render_template('login.html', form=form)



    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))



    @app.route('/order', methods=['GET', 'POST'])
    @login_required
    def order():
        menu_items = MenuItem.query.all()
        menu_item_choices = [
            (item.id, f"{item.name} (${calculate_final_price(item.base_price)})")
            for item in menu_items
        ]

        if request.method == 'GET':
            form = OrderForm()
            # Initialize the first item with choices
            if len(form.items) == 0:
                form.items.append_entry()
            for item_form in form.items:
                item_form.menu_item_id.choices = menu_item_choices
        else:
            form = OrderForm()
            form.process(request.form)
            # Set choices for each OrderItemForm
            for item_form in form.items:
                item_form.menu_item_id.choices = menu_item_choices

        if form.validate_on_submit():
            # Extract valid order items
            order_items_data = []
            for item_form in form.items:
                menu_item_id = item_form.menu_item_id.data
                quantity = item_form.quantity.data
                if menu_item_id and quantity:
                    order_items_data.append({
                        'menu_item_id': menu_item_id,
                        'quantity': quantity
                    })

            # Handle discount code
            discount_code = None
            discount_percentage = Decimal('0.00')
            discount_code_str = form.discount_code.data.strip()
            if discount_code_str:
                discount_code = DiscountCode.query.filter_by(code=discount_code_str).first()
                if not discount_code:
                    form.discount_code.errors.append('Invalid discount code.')
                    return render_template('order.html', form=form)
                else:
                    # Check if the user has already used this code
                    usage = DiscountCodeUsage.query.filter_by(
                        customer_id=current_user.id,
                        code=discount_code.code
                    ).first()
                    if usage and usage.is_used:
                        form.discount_code.errors.append('You have already used this discount code.')
                        return render_template('order.html', form=form)
                    else:
                        discount_percentage = Decimal(str(discount_code.discount_percentage))

            # Create the order
            try:
                new_order = create_order(
                    customer=current_user,
                    items=order_items_data,
                    discount_percentage=discount_percentage,
                    discount_code=discount_code
                )
                flash('Your order has been placed successfully!', 'success')
                return redirect(url_for('order_status_page', order_id=new_order.id))
            except Exception as e:
                flash(f'An error occurred while placing your order: {str(e)}', 'danger')
        else:
            if form.errors:
                for field_errors in form.errors.values():
                    for error in field_errors:
                        flash(error, 'danger')

        return render_template('order.html', form=form)



    @app.route('/order_status/<int:order_id>/status')
    @login_required
    def get_order_status(order_id):
        order = Order.query.get_or_404(order_id)
        delivery = order.delivery
        now = datetime.now()

        if delivery and delivery.estimated_delivery_time:
            time_till_delivery = delivery.estimated_delivery_time - now
            if time_till_delivery.total_seconds() > 0:
                hours, remainder = divmod(int(time_till_delivery.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                if hours > 0:
                    time_till_delivery_str = f"{hours}h {minutes}m"
                else:
                    time_till_delivery_str = f"{minutes}m"
            else:
                time_till_delivery_str = 'Any minute now!'
        else:
            time_till_delivery_str = 'Calculating...'

        print(f"Order {order_id} status: {order.status.value}")

        response = {
            'status': order.status.value,
            'delivery_personnel': delivery.delivery_personnel.name if delivery and delivery.delivery_personnel else 'Awaiting assignment',
            'estimated_delivery_time': delivery.estimated_delivery_time.strftime('%Y-%m-%d %H:%M:%S') if delivery and delivery.estimated_delivery_time else 'Calculating...',
            'time_till_delivery': time_till_delivery_str
        }
        return jsonify(response)


    
    @app.route('/order_status/<int:order_id>', methods=['GET'])
    @login_required
    def order_status_page(order_id):
        order = Order.query.get_or_404(order_id)
        
        if order.customer_id != current_user.id:
            flash('You do not have permission to view this order.', 'danger')
            return redirect(url_for('my_orders'))
        
        customer = order.customer
        now = datetime.now()
    
        # Calculate Time Till Delivery if estimated_delivery_time is available
        if order.delivery and order.delivery.estimated_delivery_time:
            time_till_delivery = order.delivery.estimated_delivery_time - now
            if time_till_delivery.total_seconds() > 0:
                hours, remainder = divmod(int(time_till_delivery.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                if hours > 0:
                    time_till_delivery_str = f"{hours}h {minutes}m"
                else:
                    time_till_delivery_str = f"{minutes}m"
            else:
                time_till_delivery_str = 'Any minute now!'
        else:
            time_till_delivery_str = 'Calculating...'
    
        return render_template(
            'order_status.html',
            order=order,
            customer=customer,
            time_till_delivery=time_till_delivery_str
        )
        

    
    @app.route('/complete_delivery/<int:delivery_id>', methods=['POST'])
    @login_required
    def complete_delivery_route(delivery_id):
        try:
            complete_delivery(delivery_id)
            flash('Delivery marked as completed.', 'success')
            delivery = Delivery.query.get(delivery_id)
            return redirect(url_for('thank_you', order_id=delivery.order_id))
        except ValueError as ve:
            flash(str(ve), 'danger')
            delivery = Delivery.query.get(delivery_id)
            return redirect(url_for('order_status_page', order_id=delivery.order_id))
        except Exception as e:
            flash('An unexpected error occurred.', 'danger')
            delivery = Delivery.query.get(delivery_id)
            return redirect(url_for('order_status_page', order_id=delivery.order_id))
        
    
    
    @app.route('/cancel_order/<int:order_id>', methods=['POST'])
    @login_required
    def cancel_order_route(order_id):
        try:
            cancel_order(order_id, current_user.id)
            flash('Your order has been cancelled.', 'success')
            return redirect(url_for('thank_you', order_id=order_id))  # Corrected redirect
        except ValueError as ve:
            flash(str(ve), 'danger')
            app.logger.warning(f"Cancellation failed for Order ID {order_id}: {ve}")
            return redirect(url_for('order_status_page', order_id=order_id))
        except Exception as e:
            flash('An unexpected error occurred while cancelling your order.', 'danger')
            app.logger.error(f"Unexpected error during cancellation of Order ID {order_id}: {e}")
            return redirect(url_for('order_status_page', order_id=order_id))


    
    @app.route('/thank_you/<int:order_id>', methods=['GET'])
    @login_required
    def thank_you(order_id):
        order = Order.query.get_or_404(order_id)
        customer = order.customer
        return render_template('thank_you.html', order=order, customer=customer)
    
                

    @app.route('/order_status_update/<int:order_id>')
    @login_required
    def order_status_update(order_id):
        order = Order.query.get_or_404(order_id)
        if order.customer_id != current_user.id:
            return {'status': 'Unauthorized'}, 403

        return {'status': order.status.value}