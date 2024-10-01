from decimal import ROUND_HALF_UP, Decimal
from flask import render_template, redirect, session, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functionality.customer import create_customer
from functionality.delivery import complete_delivery
from functionality.order import create_order
from functionality.order import cancel_order
from functionality.utils import calculate_final_price
from models import Customer, Delivery, DiscountCode, DiscountCodeUsage, MenuItem, Order, OrderItem, OrderStatusEnum, MenuItemCategoryEnum
from forms import RegistrationForm, LoginForm, OrderForm, OrderItemForm
from datetime import datetime
from flask import jsonify
from flask import request, session
from functionality.utils import calculate_final_price 

def register_routes(app):
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html')
    
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



    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            # Query the customer
            customer = Customer.query.filter_by(email=form.email.data).first()
            if customer and check_password_hash(customer.password, form.password.data):
                login_user(customer)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))  # Redirect to 'index' instead of 'order'
            else:
                flash('Invalid email or password.', 'danger')
        return render_template('login.html', form=form)




    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    

    @app.route('/menu', methods=['GET'])
    @login_required
    def menu():
        # Retrieve all menu items
        menu_items = MenuItem.query.all()

        # Optionally, categorize them
        pizzas = [item.to_dict() for item in menu_items if item.category == MenuItemCategoryEnum.Pizza]
        drinks = [item.to_dict() for item in menu_items if item.category == MenuItemCategoryEnum.Drink]
        desserts = [item.to_dict() for item in menu_items if item.category == MenuItemCategoryEnum.Dessert]

        # Render the template with the manually defined menu items
        return render_template('menu.html', pizzas=pizzas, drinks=drinks, desserts=desserts)
        
    @app.route('/order', methods=['GET', 'POST'])
    @login_required
    def order():
        discount_percentage = Decimal(session.get('discount_percentage', 0.00))
        discount_code_str = session.get('discount_code', None)
        discount_code = None  # Initialize discount_code variable

        # Initialize selected_items
        selected_items = []

        # Retrieve selected item IDs from query parameters on GET request
        if request.method == 'GET':
            selected_item_ids = request.args.getlist('item_ids')
            if selected_item_ids:
                # Convert IDs to integers
                selected_item_ids = [int(id) for id in selected_item_ids]

                # Query the database for selected items
                selected_items = MenuItem.query.filter(MenuItem.id.in_(selected_item_ids)).all()
            else:
                selected_items = []

            # Store selected_item_ids in session to preserve them between requests
            session['selected_item_ids'] = selected_item_ids

        # On POST request, retrieve selected items from session
        else:
            selected_item_ids = session.get('selected_item_ids', [])
            if selected_item_ids:
                selected_items = MenuItem.query.filter(MenuItem.id.in_(selected_item_ids)).all()
            else:
                selected_items = []

        # Calculate final price for each selected item and store in a list
        item_totals = []
        for item in selected_items:
            final_price = calculate_final_price(item.base_price)
            item.final_price = final_price  # Add final_price attribute to item for use in template
            item_totals.append(final_price)

        # Calculate subtotal
        subtotal = sum(item_totals)

        # Proceed with your existing logic
        form = OrderForm()

        # **Set up choices for form fields that require them**
        menu_items = MenuItem.query.all()
        menu_item_choices = [
            (item.id, f"{item.name} (${calculate_final_price(item.base_price)})")
            for item in menu_items
        ]

        form.process(request.form)

        # Initialize form items and set choices
        if len(form.items) == 0:
            form.items.append_entry()
        for item_form in form.items:
            item_form.menu_item_id.choices = menu_item_choices

        if form.validate_on_submit():
            # Create the order
            try:
                # Re-validate the discount code
                if discount_code_str:
                    discount_code = DiscountCode.query.filter_by(code=discount_code_str).first()
                    if discount_code:
                        # Check if the user has already used this code
                        usage = DiscountCodeUsage.query.filter_by(
                            customer_id=current_user.id,
                            code=discount_code.code
                        ).first()
                        if usage and usage.is_used:
                            flash('You have already used this discount code.', 'danger')
                            return redirect(url_for('order'))
                        else:
                            discount_percentage = Decimal(str(discount_code.discount_percentage))
                    else:
                        discount_percentage = Decimal('0.00')
                        discount_code = None
                else:
                    discount_percentage = Decimal('0.00')
                    discount_code = None

                new_order = create_order(
                    customer=current_user,
                    items=[{'menu_item_id': item.id, 'quantity': 1} for item in selected_items],
                    discount_percentage=discount_percentage,
                    discount_code=discount_code
                )
                db.session.commit()
                flash('Your order has been placed successfully!', 'success')
                # Clear selected items and discount from session
                session.pop('selected_item_ids', None)
                session.pop('discount_code', None)
                session.pop('discount_percentage', None)
                return redirect(url_for('order_status_page', order_id=new_order.id))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while placing your order: {str(e)}', 'danger')
        else:
            # Handle form validation errors or initial GET request
            pass

        # Calculate discount amount and total after discount
        discount_amount = (subtotal * (discount_percentage / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_after_discount = (subtotal - discount_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Debugging statements
        print("Order Summary:")
        print(f"Subtotal: ${subtotal}")
        print(f"Discount Percentage: {discount_percentage}%")
        print(f"Discount Amount: -${discount_amount}")
        print(f"Total After Discount: ${total_after_discount}")

        return render_template(
            'order.html',
            selected_items=selected_items,
            form=form,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_after_discount=total_after_discount,
            discount_percentage=discount_percentage
        )

    @app.route('/apply_discount', methods=['POST'])
    @login_required
    def apply_discount():
        data = request.get_json()
        discount_code_str = data.get('discount_code', '').strip()

        # Validate the discount code
        discount_code = DiscountCode.query.filter_by(code=discount_code_str).first()
        if not discount_code:
            print(f"Discount code '{discount_code_str}' is invalid.")  # Debugging line
            return jsonify({'success': False, 'message': 'Invalid discount code.'}), 400

        # Check if the user has already used this code
        usage = DiscountCodeUsage.query.filter_by(
            customer_id=current_user.id,
            code=discount_code.code
        ).first()
        if usage and usage.is_used:
            print(f"Discount code '{discount_code_str}' has already been used by user {current_user.id}.")  # Debugging line
            return jsonify({'success': False, 'message': 'You have already used this discount code.'}), 400

        # Calculate the new total with the discount applied
        discount_percentage = discount_code.discount_percentage

        # Retrieve selected items from session
        selected_item_ids = session.get('selected_item_ids', [])
        selected_items = MenuItem.query.filter(MenuItem.id.in_(selected_item_ids)).all()

        # Calculate final prices
        item_totals = [calculate_final_price(item.base_price) for item in selected_items]
        subtotal = sum(item_totals)

        # Apply the discount
        discount_amount = (subtotal * (discount_percentage / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_after_discount = (subtotal - discount_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Debugging statements
        print(f"Discount Code Applied: {discount_code_str}")
        print(f"Discount Percentage: {discount_percentage}%")
        print(f"Subtotal before discount: ${subtotal}")
        print(f"Discount Amount: -${discount_amount}")
        print(f"Total after discount: ${total_after_discount}")

        # Store the discount code and percentage in the session
        session['discount_code'] = discount_code_str
        session['discount_percentage'] = float(discount_percentage)

        # Respond with updated values
        return jsonify({
            'success': True,
            'subtotal': float(subtotal),
            'discount_percentage': float(discount_percentage),
            'discount_amount': float(discount_amount),
            'total_after_discount': float(total_after_discount)
        })

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