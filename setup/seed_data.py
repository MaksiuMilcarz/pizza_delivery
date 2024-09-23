from datetime import datetime
from decimal import Decimal
from setup.extensions import db
from models import Customer, DeliveryPersonnel, DiscountCode, GenderEnum, Ingredient, MenuItem, MenuItemCategoryEnum
from werkzeug.security import generate_password_hash

def seed_data():
    # Check if the database is already seeded
    if MenuItem.query.first():
        print("Database already seeded.")
        return

    # Seed Ingredients
    ingredients = [
        Ingredient(name='Tomato Sauce', base_price=0.50, is_vegan=True, is_vegetarian=True),
        Ingredient(name='Mozzarella', base_price=1.00, is_vegan=False, is_vegetarian=True),
        Ingredient(name='Pepperoni', base_price=1.50, is_vegan=False, is_vegetarian=False),
        Ingredient(name='Mushrooms', base_price=0.75, is_vegan=True, is_vegetarian=True),
        Ingredient(name='Olives', base_price=0.60, is_vegan=True, is_vegetarian=True),
        Ingredient(name='Onions', base_price=0.40, is_vegan=True, is_vegetarian=True),
        Ingredient(name='Bell Peppers', base_price=0.50, is_vegan=True, is_vegetarian=True),
        Ingredient(name='Pineapple', base_price=0.70, is_vegan=True, is_vegetarian=True),
        Ingredient(name='Bacon', base_price=1.20, is_vegan=False, is_vegetarian=False),
        Ingredient(name='Spinach', base_price=0.80, is_vegan=True, is_vegetarian=True)
    ]
    db.session.add_all(ingredients)
    db.session.commit()
    print("Ingredients seeded.")

    # Seed Menu Items (Pizzas)
    pizzas = [
        MenuItem(name='Margherita', category=MenuItemCategoryEnum.Pizza, base_price=5.00, is_vegetarian=True),
        MenuItem(name='Pepperoni', category=MenuItemCategoryEnum.Pizza, base_price=6.50, is_vegetarian=False),
        MenuItem(name='Vegan Delight', category=MenuItemCategoryEnum.Pizza, base_price=7.00, is_vegan=True, is_vegetarian=True),
        MenuItem(name='Hawaiian', category=MenuItemCategoryEnum.Pizza, base_price=6.00, is_vegetarian=False),
        MenuItem(name='Mushroom', category=MenuItemCategoryEnum.Pizza, base_price=5.50, is_vegetarian=True),
        MenuItem(name='BBQ Chicken', category=MenuItemCategoryEnum.Pizza, base_price=7.50, is_vegetarian=False),
        MenuItem(name='Spinach & Feta', category=MenuItemCategoryEnum.Pizza, base_price=6.00, is_vegetarian=True),
        MenuItem(name='Four Cheese', category=MenuItemCategoryEnum.Pizza, base_price=6.50, is_vegetarian=True),
        MenuItem(name='Supreme', category=MenuItemCategoryEnum.Pizza, base_price=8.00, is_vegetarian=False),
        MenuItem(name='Mediterranean', category=MenuItemCategoryEnum.Pizza, base_price=7.00, is_vegetarian=True)
    ]
    db.session.add_all(pizzas)
    db.session.commit()
    print("Pizzas seeded.")

    # Associate Pizzas with Ingredients
    pizzas[0].ingredients.extend([ingredients[0], ingredients[1]])  # Margherita
    pizzas[1].ingredients.extend([ingredients[0], ingredients[1], ingredients[2]])  # Pepperoni
    pizzas[2].ingredients.extend([ingredients[0], ingredients[3], ingredients[4], ingredients[9]])  # Vegan Delight
    pizzas[3].ingredients.extend([ingredients[0], ingredients[1], ingredients[4], ingredients[7]])  # Hawaiian
    pizzas[4].ingredients.extend([ingredients[0], ingredients[1], ingredients[3]])  # Mushroom
    pizzas[5].ingredients.extend([ingredients[0], ingredients[1], ingredients[6], ingredients[8]])  # BBQ Chicken
    pizzas[6].ingredients.extend([ingredients[0], ingredients[9], ingredients[1]])  # Spinach & Feta
    pizzas[7].ingredients.extend([ingredients[0], ingredients[1], ingredients[5], ingredients[9]])  # Four Cheese
    pizzas[8].ingredients.extend([ingredients[0], ingredients[1], ingredients[2], ingredients[3], ingredients[4], ingredients[6]])  # Supreme
    pizzas[9].ingredients.extend([ingredients[0], ingredients[1], ingredients[3], ingredients[4], ingredients[5]])  # Mediterranean

    db.session.commit()
    print("Pizza-Ingredients associations seeded.")

    # Seed Drinks
    drinks = [
        MenuItem(name='Coca Cola', category=MenuItemCategoryEnum.Drink, base_price=1.50),
        MenuItem(name='Sprite', category=MenuItemCategoryEnum.Drink, base_price=1.50),
        MenuItem(name='Water', category=MenuItemCategoryEnum.Drink, base_price=1.00),
        MenuItem(name='Orange Juice', category=MenuItemCategoryEnum.Drink, base_price=2.00)
    ]
    db.session.add_all(drinks)
    db.session.commit()
    print("Drinks seeded.")

    # Seed Desserts
    desserts = [
        MenuItem(name='Tiramisu', category=MenuItemCategoryEnum.Dessert, base_price=3.50),
        MenuItem(name='Gelato', category=MenuItemCategoryEnum.Dessert, base_price=2.50)
    ]
    db.session.add_all(desserts)
    db.session.commit()
    print("Desserts seeded.")
    
    # Seed a Customer
    customer = Customer(
        name='Max Milcarz',
        gender=GenderEnum.Male,
        birthdate=datetime(2004, 2, 2),
        phone='1234567890',
        address='Sorbonnelaan 182',
        postal_code='6229',
        email='max.milcarz@yahoo.com',
        password=generate_password_hash('passward'),
        total_pizzas_ordered=0,
        birthday_pizza_claimed=False
    )
    db.session.add(customer)
    db.session.commit()
    print("Customer seeded.")
    
    # Seed Discount Codes
    discount_codes = [
        DiscountCode(
            code='WELCOME10',
            discount_percentage=Decimal('10.00')
        ),
        DiscountCode(
            code='SUMMER20',
            discount_percentage=Decimal('20.00')
        ),
        DiscountCode(
            code='VIP30',
            discount_percentage=Decimal('30.00')
        ),
        DiscountCode(
            code='123',
            discount_percentage=Decimal('20.00')
        ),
        DiscountCode(
            code='12345',
            discount_percentage=Decimal('30.00')
        )
    ]
    db.session.add_all(discount_codes)
    db.session.commit()
    print("Codes seeded.")
    
    delivery_personnel_list = [
        DeliveryPersonnel(name='Alice', phone='0111111111', postal_code=None, is_available=True),
        DeliveryPersonnel(name='Bob', phone='0222222222', postal_code=None, is_available=True),
        DeliveryPersonnel(name='Charlie', phone='0333333333', postal_code=None, is_available=True),
        DeliveryPersonnel(name='Diana', phone='04444444444', postal_code=None, is_available=True),
    ]
    db.session.add_all(delivery_personnel_list)
    db.session.commit()
    print("Delivery Personnel seeded.")