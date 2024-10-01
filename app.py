from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import webbrowser
from threading import Timer
from sqlalchemy.exc import IntegrityError
from setup.extensions import db, login_manager
from routes import register_routes 
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'passward'  # Replace with a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizza_delivery.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Bind SQLAlchemy and LoginManager to the app using init_app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

# Define the user_loader callback
from models import Customer
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Customer, int(user_id))

# Register all routes
register_routes(app)

# Import models and seed data after initializing db and login_manager
with app.app_context():
    from models import * 
    from setup.seed_data import seed_data 
    
scheduler = APScheduler()  
scheduler.init_app(app)
def update_pending_deliveries_task():
    with app.app_context():
        from functionality.delivery import update_pending_deliveries
        update_pending_deliveries()  
scheduler.start() 

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/login')
if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        db.create_all()     
        seed_data()       
    Timer(1, open_browser).start()  
    app.run(debug=True)
