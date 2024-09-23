from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create the SQLAlchemy and LoginManager instances
db = SQLAlchemy()
login_manager = LoginManager()
