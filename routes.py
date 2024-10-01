from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request
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
        # Manually define the menu items
        pizzas = [
            {"id": 1, "name": "Margherita", "base_price": 5.00, "image": "margherita.jpeg", 
             "description": "Classic delight with 100% real mozzarella cheese", "is_vegetarian": True, "is_vegan": False},
            {"id": 2, "name": "Pepperoni", "base_price": 6.50, "image": "pepperoni.jpeg", 
             "description": "Loaded with pepperoni and cheese", "is_vegetarian": False, "is_vegan": False},
            {"id": 3, "name": "Vegan Delight", "base_price": 7.00, "image": "vegan_delight.jpeg", 
             "description": "A healthy choice with fresh vegetables", "is_vegetarian": True, "is_vegan": True},
            {"id": 4, "name": "Hawaiian", "base_price": 6.00, "image": "hawaiian.jpeg", 
             "description": "Ham, pineapple, and mozzarella cheese", "is_vegetarian": False, "is_vegan": False},
            {"id": 5, "name": "Mushroom", "base_price": 5.50, "image": "mushroom.jpeg", 
             "description": "Loaded with mushrooms and mozzarella cheese", "is_vegetarian": True, "is_vegan": False},
            {"id": 6, "name": "BBQ Chicken", "base_price": 7.50, "image": "bbq_chicken.jpeg", 
             "description": "BBQ sauce, chicken, and onions", "is_vegetarian": False, "is_vegan": False},
            {"id": 7, "name": "Spinach & Feta", "base_price": 6.00, "image": "spinach_feta.jpeg", 
             "description": "Spinach, feta cheese, and mozzarella", "is_vegetarian": True, "is_vegan": False},
            {"id": 8, "name": "Four Cheese", "base_price": 6.50, "image": "four_cheese.jpeg", 
             "description": "A blend of four cheeses", "is_vegetarian": True, "is_vegan": False},
            {"id": 9, "name": "Supreme", "base_price": 8.00, "image": "supreme.jpeg", 
             "description": "Pepperoni, mushrooms, bell peppers, and onions", "is_vegetarian": False, "is_vegan": False},
            {"id": 10, "name": "Mediterranean", "base_price": 7.00, "image": "mediterranean.png", 
             "description": "Olives, feta, and bell peppers", "is_vegetarian": True, "is_vegan": False}
        ]

        drinks = [
            {"id": 11, "name": "Coca Cola", "base_price": 1.50, "image": "coca_cola.jpeg", 
             "description": "Refreshing Coca Cola"},
            {"id": 12, "name": "Sprite", "base_price": 1.50, "image": "sprite.jpeg", 
             "description": "Lemon-lime flavored soda"},
            {"id": 13, "name": "Water", "base_price": 1.00, "image": "water.jpeg", 
             "description": "Pure and clean bottled water"},
            {"id": 14, "name": "Orange Juice", "base_price": 2.00, "image": "orange_juice.jpeg", 
             "description": "Freshly squeezed orange juice"}
        ]

        desserts = [
            {"id": 15, "name": "Tiramisu", "base_price": 3.50, "image": "tiramisu.jpeg", 
             "description": "Classic Italian dessert with mascarpone"},
            {"id": 16, "name": "Gelato", "base_price": 2.50, "image": "gelato.jpeg", 
             "description": "Creamy Italian ice cream"}
        ]


        # Render the template with the manually defined menu items
        return render_template('menu.html', pizzas=pizzas, drinks=drinks, desserts=desserts)
    

    @app.route('/order', methods=['GET', 'POST'])
    @login_required
    def order():
        from setup.extensions import db
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
            # Process form submission
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
                    items=[{'menu_item_id': item.id, 'quantity': 1} for item in selected_items],
                    discount_percentage=discount_percentage,
                    discount_code=discount_code
                )
                db.session.commit()
                flash('Your order has been placed successfully!', 'success')
                return redirect(url_for('order_status_page', order_id=new_order.id))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while placing your order: {str(e)}', 'danger')
        else:
            # Initial rendering or form validation failed
            pass

        return render_template('order.html', selected_items=selected_items, form=form, discount_percentage=discount_percentage)



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