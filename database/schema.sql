-- drop all tables from the database
DROP DATABASE PizzaOrderingSystem;
CREATE DATABASE PizzaOrderingSystem;
USE PizzaOrderingSystem;


CREATE TABLE MenuItem (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    category ENUM('Pizza', 'Drink', 'Dessert') NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE
);
CREATE TABLE Ingredient (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE
);
CREATE TABLE MenuItemIngredient (
    menu_item_id INT,
    ingredient_id INT,
    PRIMARY KEY (menu_item_id, ingredient_id),
    FOREIGN KEY (menu_item_id) REFERENCES MenuItem(id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(id)
);
CREATE TABLE Customer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    birthdate DATE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address TEXT NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- Use hashed passwords
    total_pizzas_ordered INT DEFAULT 0,
    birthday_pizza_claimed BOOLEAN DEFAULT FALSE
);
CREATE TABLE `Order` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_time TIMESTAMP,
    total_price DECIMAL(10, 2) NOT NULL,
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    status ENUM('Pending', 'Being Prepared', 'In Process', 'Out for Delivery', 'Delivered', 'Cancelled') NOT NULL DEFAULT 'Pending',
    is_cancelled BOOLEAN DEFAULT FALSE,
    cancellation_time TIMESTAMP NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(id)
);
CREATE TABLE OrderItem (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (menu_item_id) REFERENCES MenuItem(id)
);
CREATE TABLE DiscountCode (
    code VARCHAR(20) PRIMARY KEY,
    discount_percentage DECIMAL(5, 2) NOT NULL
);
CREATE TABLE DiscountCodeUsage (
    customer_id INT,
    code VARCHAR(20),
    is_used BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (customer_id, code),
    FOREIGN KEY (customer_id) REFERENCES Customer(id),
    FOREIGN KEY (code) REFERENCES DiscountCode(code)
);
CREATE TABLE DeliveryPersonnel (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    last_delivery_time TIMESTAMP NULL
);
CREATE TABLE Delivery (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    delivery_personnel_id INT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Being Prepared', 'In Process', 'Out for Delivery', 'Delivered', 'Cancelled') DEFAULT 'Being Prepared',
    estimated_delivery_time TIMESTAMP,
    delivery_time TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (delivery_personnel_id) REFERENCES DeliveryPersonnel(id)
);
CREATE TABLE OrderStatusHistory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    status ENUM('Pending', 'Being Prepared', 'In Process', 'Out for Delivery', 'Delivered', 'Cancelled') NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);

