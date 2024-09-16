# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'root')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'IlikeKatyPerry')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', '3306')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'PizzaOrderingSystem')
