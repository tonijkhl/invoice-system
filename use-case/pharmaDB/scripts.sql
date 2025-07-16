CREATE DATABASE parhma-db;

-- Create essential tables only
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    insurance_provider VARCHAR(100),
    insurance_number VARCHAR(50)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(100) NOT NULL,
    generic_name VARCHAR(100),
    strength VARCHAR(50),
    form VARCHAR(50),
    selling_price DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 0
);

CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Pending'
);

CREATE TABLE invoice_items (
    invoice_item_id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

-- Create index for better performance
CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_product ON invoice_items(product_id);


-- Insert more sample customers
INSERT INTO customers (first_name, last_name, phone, email, address, insurance_provider, insurance_number)
VALUES 
('Alice', 'Walker', '555-234-5678', 'alice.walker@email.com', '456 Maple Ave, Townsville', 'HealthFirst', 'HF112233'),
('Bob', 'Johnson', '555-345-6789', 'bob.j@email.com', '789 Oak Blvd, Metropolis', 'MediCare', 'MC445566'),
('Carol', 'Davis', '555-456-7890', 'carol.d@email.com', '321 Pine Dr, Smalltown', 'BlueShield', 'BS778899'),
('David', 'Lee', '555-567-8901', 'david.lee@email.com', '654 Cedar Ln, Rivertown', 'HealthNet', 'HN998877'),
('Eva', 'Green', '555-678-9012', 'eva.green@email.com', '987 Spruce St, Uptown', 'Aetna', 'AE556677'),
('Frank', 'White', '555-789-0123', 'frank.w@email.com', '111 Birch Rd, Suburbia', 'WellCare', 'WC334455'),
('Grace', 'Kim', '555-890-1234', 'grace.kim@email.com', '222 Walnut St, Oldcity', 'HealthPlus', 'HP123321'),
('Henry', 'Nguyen', '555-901-2345', 'henry.n@email.com', '333 Aspen Ct, Midtown', 'Humana', 'HU456654'),
('Ivy', 'Martinez', '555-012-3456', 'ivy.m@email.com', '444 Cypress Rd, Newville', 'Cigna', 'CI789987');

-- Insert more products
INSERT INTO products (product_code, product_name, generic_name, strength, form, selling_price, tax_rate)
VALUES 
('PAR500', 'Paracetamol', 'Acetaminophen', '500mg', 'Tablet', 9.50, 0.05),
('VITA-C', 'Vitamin C', 'Ascorbic Acid', '1000mg', 'Tablet', 11.25, 0.00),
('LOR10', 'Loratadine', 'Loratadine', '10mg', 'Tablet', 7.40, 0.05),
('OMZ20', 'Omeprazole', 'Omeprazole', '20mg', 'Capsule', 13.10, 0.05),
('AZT250', 'Azithromycin', 'Azithromycin', '250mg', 'Tablet', 22.00, 0.05),
('MET500', 'Metformin', 'Metformin', '500mg', 'Tablet', 10.80, 0.00),
('ALB400', 'Albendazole', 'Albendazole', '400mg', 'Tablet', 14.30, 0.05),
('HIST5', 'Diphenhydramine', 'Diphenhydramine', '25mg', 'Capsule', 6.70, 0.00),
('RANT150', 'Ranitidine', 'Ranitidine', '150mg', 'Tablet', 12.60, 0.05),
('DOX100', 'Doxycycline', 'Doxycycline', '100mg', 'Capsule', 19.75, 0.05);

-- Insert more invoices
INSERT INTO invoices (customer_id, invoice_number, subtotal, tax_amount, discount_amount, total_amount, payment_status)
VALUES 
(2, 'PHARM-2023-002', 25.00, 1.25, 0.00, 26.25, 'Paid'),
(3, 'PHARM-2023-003', 41.25, 2.06, 0.00, 43.31, 'Pending'),
(4, 'PHARM-2023-004', 30.60, 1.53, 0.00, 32.13, 'Paid'),
(5, 'PHARM-2023-005', 19.90, 0.99, 0.00, 20.89, 'Paid'),
(6, 'PHARM-2023-006', 38.00, 1.90, 2.00, 37.90, 'Pending'),
(7, 'PHARM-2023-007', 45.10, 2.26, 0.00, 47.36, 'Pending'),
(8, 'PHARM-2023-008', 52.00, 2.60, 5.00, 49.60, 'Paid'),
(9, 'PHARM-2023-009', 18.20, 0.91, 0.00, 19.11, 'Paid'),
(10, 'PHARM-2023-010', 60.50, 3.03, 0.00, 63.53, 'Pending'),
(11, 'PHARM-2023-011', 34.25, 1.71, 0.00, 35.96, 'Paid');

-- Insert corresponding invoice_items
INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, tax_rate, total_price)
VALUES 
-- Invoice 2
(2, 4, 2, 13.10, 0.05, 26.20),
-- Invoice 3
(3, 5, 1, 22.00, 0.05, 22.00),
(3, 2, 2, 8.99, 0.05, 17.98),
-- Invoice 4
(4, 6, 2, 10.80, 0.00, 21.60),
(4, 1, 1, 12.99, 0.05, 12.99),
-- Invoice 5
(5, 3, 1, 15.99, 0.00, 15.99),
(5, 9, 1, 12.60, 0.05, 12.60),
-- Invoice 6
(6, 10, 2, 19.75, 0.05, 39.50),
-- Invoice 7
(7, 7, 1, 14.30, 0.05, 14.30),
(7, 8, 2, 6.70, 0.00, 13.40),
(7, 1, 1, 12.99, 0.05, 12.99),
-- Invoice 8
(8, 4, 2, 13.10, 0.05, 26.20),
(8, 5, 1, 22.00, 0.05, 22.00),
-- Invoice 9
(9, 2, 2, 8.99, 0.05, 17.98),
-- Invoice 10
(10, 10, 3, 19.75, 0.05, 59.25),
-- Invoice 11
(11, 3, 2, 15.99, 0.00, 31.98),
(11, 6, 1, 10.80, 0.00, 10.80);
