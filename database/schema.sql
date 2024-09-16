-- drop all tables from the database
DROP DATABASE PizzaOrderingSystem;
CREATE DATABASE PizzaOrderingSystem;
USE PizzaOrderingSystem;


-- Stores information about available pizzas, including their price and dietary restrictions.
CREATE TABLE Pizza (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE
);

-- Contains all available ingredients and their details such as price and dietary information.
CREATE TABLE Ingredient (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE
);

-- Relates pizzas to their ingredients, allowing many-to-many relationships between pizzas and ingredients.
CREATE TABLE Pizza_Ingredients (
    pizza_id INT,
    ingredient_id INT,
    PRIMARY KEY (pizza_id, ingredient_id),
    FOREIGN KEY (pizza_id) REFERENCES Pizza(id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(id)
);

-- Stores information about drinks available for ordering.
CREATE TABLE Drink (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL
);

-- Stores information about desserts available for ordering.
CREATE TABLE Dessert (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL
);

-- Stores customer information, including login credentials and their order history.
CREATE TABLE Customer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    birthdate DATE NOT NULL,
    phone VARCHAR(12) NOT NULL,
    address TEXT NOT NULL,
    postal_code INT NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(20) NOT NULL,
    total_pizzas_ordered INT DEFAULT 0,
    birthday_pizza_claimed BOOLEAN DEFAULT FALSE
);

-- Stores details about customer orders, including delivery status and applied discounts.
CREATE TABLE `Order` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_time TIMESTAMP,
    discount_applied BOOLEAN DEFAULT FALSE,
    birthday_offer_applied BOOLEAN DEFAULT FALSE,
    discount_code_used BOOLEAN DEFAULT FALSE,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('Pending', 'Dispatched', 'Delivered') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (customer_id) REFERENCES Customer(id)
);

-- Relates orders to the pizzas ordered, along with their quantity and price.
CREATE TABLE Order_Pizzas (
    order_id INT,
    pizza_id INT,
    quantity INT DEFAULT 1,
    price DECIMAL(10, 2),
    PRIMARY KEY (order_id, pizza_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (pizza_id) REFERENCES Pizza(id)
);

-- Relates orders to the drinks ordered, including quantity and price.
CREATE TABLE Order_Drinks (
    order_id INT,
    drink_id INT,
    quantity INT DEFAULT 1,
    price DECIMAL(10, 2),
    PRIMARY KEY (order_id, drink_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (drink_id) REFERENCES Drink(id)
);

-- Relates orders to the desserts ordered, along with their quantity and price.
CREATE TABLE Order_Desserts (
    order_id INT,
    dessert_id INT,
    quantity INT DEFAULT 1,
    price DECIMAL(10, 2),
    PRIMARY KEY (order_id, dessert_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (dessert_id) REFERENCES Dessert(id)
);

-- Stores available discount codes and the percentage discount they provide.
CREATE TABLE Discount_Codes (
    code VARCHAR(20) PRIMARY KEY,
    discount_percentage DECIMAL(5, 2) NOT NULL
);

-- Tracks if a customer has used a specific discount code.
CREATE TABLE Discount_Codes_Used (
    customer_id INT,
    code VARCHAR(20),
    is_used BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (customer_id, code),
    FOREIGN KEY (customer_id) REFERENCES Customer(id),
    FOREIGN KEY (code) REFERENCES Discount_Codes(code)
);

-- Stores confirmation information for an order, including delivery estimates.
CREATE TABLE Order_Confirmation (
    order_id INT PRIMARY KEY,
    confirmation_text TEXT,
    estimated_delivery_time TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);

-- Stores information about delivery personnel, including their assigned postal code and availability.
CREATE TABLE Delivery_Personnel (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    phone VARCHAR(12) NOT NULL,
    postal_code INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

-- Stores information about individual deliveries, including the delivery person assigned and delivery status.
CREATE TABLE Delivery (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    delivery_personnel_id INT,
    status ENUM('Being Prepared', 'In Process', 'Out for Delivery', 'Delivered', 'Cancelled') DEFAULT 'Being Prepared',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_delivery_time TIMESTAMP,
    delivery_time TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (delivery_personnel_id) REFERENCES Delivery_Personnel(id)
);

-- Tracks if and when an order was cancelled.
CREATE TABLE Order_Cancellation (
    order_id INT PRIMARY KEY,
    cancellation_time TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);

-- Groups multiple deliveries by postal code to be handled by one delivery person.
CREATE TABLE Delivery_Grouping (
    group_id INT PRIMARY KEY AUTO_INCREMENT,
    delivery_personnel_id INT,
    postal_code INT,
    group_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (delivery_personnel_id) REFERENCES Delivery_Personnel(id)
);

-- Relates grouped deliveries to individual orders.
CREATE TABLE Grouped_Orders (
    group_id INT,
    order_id INT,
    PRIMARY KEY (group_id, order_id),
    FOREIGN KEY (group_id) REFERENCES Delivery_Grouping(group_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);

-- Provides a status update for customers, showing the current state of their order.
CREATE TABLE Customer_Order_Status (
    order_id INT PRIMARY KEY,
    status_text VARCHAR(255),
    estimated_delivery_time TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);
