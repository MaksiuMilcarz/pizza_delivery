from flask import flash
from setup.extensions import db, login_manager
from models import Customer

def create_customer(form,hashed_password):        
        new_customer = Customer(
            name=form.name.data,
            gender=form.gender.data,
            birthdate=form.birthdate.data,
            phone=form.phone.data,
            address=form.address.data,
            postal_code=form.postal_code.data,
            email=form.email.data,
            password=hashed_password
        )
        
        # Add to the database
        db.session.add(new_customer)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')   
        return new_customer