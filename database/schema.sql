USE PizzaOrderingSystem;

CREATE TABLE Pizza (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each pizza
    name VARCHAR(50) NOT NULL,         -- Name of the pizza (e.g., Margherita, Pepperoni)
    base_price DECIMAL(10, 2) NOT NULL, -- Base price for the pizza
    is_vegan BOOLEAN DEFAULT FALSE,     -- Is the pizza vegan?
    is_vegetarian BOOLEAN DEFAULT FALSE -- Is the pizza vegetarian?
);
CREATE TABLE Ingredient (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each ingredient
    name VARCHAR(50) NOT NULL,        -- Name of the ingredient (e.g., Cheese, Tomato)
    base_price DECIMAL(10, 2) NOT NULL, -- Price of the ingredient
    is_vegan BOOLEAN DEFAULT FALSE,    -- Is the ingredient vegan?
    is_vegetarian BOOLEAN DEFAULT FALSE -- Is the ingredient vegetarian?
);
CREATE TABLE Pizza_Ingredients (
    pizza_id INT,                      -- Foreign Key referencing Pizza table
    ingredient_id INT,                 -- Foreign Key referencing Ingredient table
    PRIMARY KEY (pizza_id, ingredient_id),
    FOREIGN KEY (pizza_id) REFERENCES Pizza(id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(id)
);
CREATE TABLE Drink (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each drink
    name VARCHAR(50) NOT NULL,         -- Name of the drink (e.g., Coke, Water)
    base_price DECIMAL(10, 2) NOT NULL  -- Price of the drink
);
CREATE TABLE Dessert (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each dessert
    name VARCHAR(50) NOT NULL,         -- Name of the dessert (e.g., Ice Cream, Cake)
    base_price DECIMAL(10, 2) NOT NULL  -- Price of the dessert
);
CREATE TABLE Customer (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each customer
    name VARCHAR(50) NOT NULL,         -- Customer's name
    gender ENUM('Male', 'Female', 'Other') NOT NULL, -- Gender of the customer
    birthdate DATE NOT NULL,            -- Birthdate of the customer
    phone VARCHAR(20) NOT NULL,         -- Phone number
    address TEXT NOT NULL,              -- Address for delivery
    email VARCHAR(100) UNIQUE NOT NULL, -- Email for login
    password VARCHAR(100) NOT NULL,     -- Password for login (hashed)
    total_pizzas_ordered INT DEFAULT 0, -- Number of pizzas ordered by the customer
    birthday_pizza_claimed BOOLEAN DEFAULT FALSE -- True if birthday pizza offer has been claimed
);
CREATE TABLE `Order` (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for each order
    customer_id INT,                    -- Foreign Key referencing Customer table
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of when the order was placed
    delivery_time TIMESTAMP,            -- Estimated delivery time
    discount_applied BOOLEAN DEFAULT FALSE, -- If a 10% discount was applied
    birthday_offer_applied BOOLEAN DEFAULT FALSE, -- If a birthday offer was applied
    discount_code_used BOOLEAN DEFAULT FALSE, -- If a discount code was used
    total_price DECIMAL(10, 2) NOT NULL, -- Final price of the order
    status ENUM('Pending', 'Dispatched', 'Delivered') NOT NULL DEFAULT 'Pending', -- Status of the order
    FOREIGN KEY (customer_id) REFERENCES Customer(id)
);

CREATE TABLE Order_Pizzas (
    order_id INT,                      -- Foreign Key referencing Order table
    pizza_id INT,                      -- Foreign Key referencing Pizza table
    quantity INT DEFAULT 1,            -- Number of pizzas in this order
    price DECIMAL(10, 2),              -- Price of the pizza (could include discounts)
    PRIMARY KEY (order_id, pizza_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (pizza_id) REFERENCES Pizza(id)
);
CREATE TABLE Order_Drinks (
    order_id INT,                      -- Foreign Key referencing Order table
    drink_id INT,                      -- Foreign Key referencing Drink table
    quantity INT DEFAULT 1,            -- Number of drinks in this order
    price DECIMAL(10, 2),              -- Price of the drink
    PRIMARY KEY (order_id, drink_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (drink_id) REFERENCES Drink(id)
);
CREATE TABLE Order_Desserts (
    order_id INT,                      -- Foreign Key referencing Order table
    dessert_id INT,                    -- Foreign Key referencing Dessert table
    quantity INT DEFAULT 1,            -- Number of desserts in this order
    price DECIMAL(10, 2),              -- Price of the dessert
    PRIMARY KEY (order_id, dessert_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (dessert_id) REFERENCES Dessert(id)
);
CREATE TABLE Discount_Codes (
    code VARCHAR(50) PRIMARY KEY,       -- Unique discount code
    discount_percentage DECIMAL(5, 2) NOT NULL -- Percentage discount offered (e.g., 10.00 for 10%)
);
CREATE TABLE Discount_Codes_Used (
    customer_id INT,                   -- Foreign Key referencing Customer table
    code VARCHAR(50),                  -- Foreign Key referencing Discount_Codes table
    is_used BOOLEAN DEFAULT FALSE,     -- Tracks if the discount code has been used
    PRIMARY KEY (customer_id, code),
    FOREIGN KEY (customer_id) REFERENCES Customer(id),
    FOREIGN KEY (code) REFERENCES Discount_Codes(code)
);
CREATE TABLE Order_Confirmation (
    order_id INT PRIMARY KEY,          -- Foreign Key referencing Order table
    confirmation_text TEXT,            -- Text containing the order confirmation
    estimated_delivery_time TIMESTAMP, -- The estimated delivery time for the order
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);
CREATE TABLE Delivery_Personnel (
    id INT PRIMARY KEY AUTO_INCREMENT,           -- Unique identifier for each delivery person
    name VARCHAR(50) NOT NULL,                   -- Name of the delivery person
    phone VARCHAR(20) NOT NULL,                   -- Phone number for contact
    postal_code VARCHAR(20) NOT NULL,             -- Assigned postal code area
    is_available BOOLEAN DEFAULT TRUE             -- True if available for delivery, false if currently delivering
);
CREATE TABLE Delivery (
    id INT PRIMARY KEY AUTO_INCREMENT,          -- Unique delivery identifier
    order_id INT,                                -- Foreign Key referencing Order table
    delivery_personnel_id INT,                   -- Foreign Key referencing Delivery_Personnel table
    status ENUM('Being Prepared', 'In Process', 'Out for Delivery', 'Delivered', 'Cancelled') DEFAULT 'Being Prepared', -- Status of the order delivery
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Time when the delivery was assigned
    estimated_delivery_time TIMESTAMP,           -- Estimated delivery time
    delivery_time TIMESTAMP,                     -- Actual delivery completion time
    FOREIGN KEY (order_id) REFERENCES `Order`(id),
    FOREIGN KEY (delivery_personnel_id) REFERENCES Delivery_Personnel(id)
);
CREATE TABLE Order_Cancellation (
    order_id INT PRIMARY KEY,                    -- Foreign Key referencing Order table
    cancellation_time TIMESTAMP,                 -- The time when the order was cancelled
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);
CREATE TABLE Delivery_Grouping (
    group_id INT PRIMARY KEY AUTO_INCREMENT,     -- Unique identifier for a group of deliveries
    delivery_personnel_id INT,                   -- Foreign Key referencing Delivery_Personnel table
    postal_code VARCHAR(20),                     -- Postal code for which the orders are grouped
    group_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- The time when the first order in the group was placed
    FOREIGN KEY (delivery_personnel_id) REFERENCES Delivery_Personnel(id)
);
CREATE TABLE Grouped_Orders (
    group_id INT,                                -- Foreign Key referencing Delivery_Grouping table
    order_id INT,                                -- Foreign Key referencing Order table
    PRIMARY KEY (group_id, order_id),
    FOREIGN KEY (group_id) REFERENCES Delivery_Grouping(group_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);
CREATE TABLE Customer_Order_Status (
    order_id INT PRIMARY KEY,                   -- Foreign Key referencing Order table
    status_text VARCHAR(255),                   -- Description of the current status (e.g., "Your order is being prepared")
    estimated_delivery_time TIMESTAMP,          -- Estimated delivery time displayed to the customer
    FOREIGN KEY (order_id) REFERENCES `Order`(id)
);

