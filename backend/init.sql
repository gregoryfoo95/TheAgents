-- Create database schema for property marketplace

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    user_type VARCHAR(20) CHECK (user_type IS NULL OR user_type IN ('consumer', 'agent', 'lawyer')),
    oauth_provider VARCHAR(50) NOT NULL DEFAULT 'google',
    oauth_id VARCHAR(255) NOT NULL,
    profile_picture_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Addresses table (normalized)
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    street_address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties table (normalized)
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    address_id INTEGER REFERENCES addresses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    property_type VARCHAR(50) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    ai_estimated_price DECIMAL(12, 2),
    bedrooms INTEGER,
    bathrooms INTEGER,
    square_feet INTEGER,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'pending', 'sold', 'withdrawn')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property images table (normalized)
CREATE TABLE IF NOT EXISTS property_images (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property features table
CREATE TABLE IF NOT EXISTS property_features (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    feature_name VARCHAR(100) NOT NULL,
    feature_value VARCHAR(255)
);

-- Chat conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    buyer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    lawyer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'document', 'image')),
    file_url VARCHAR(500),
    file_name VARCHAR(255),
    file_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Viewing bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    buyer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lawyers table (extended user information for lawyers)
CREATE TABLE IF NOT EXISTS lawyer_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    firm_name VARCHAR(255) NOT NULL,
    license_number VARCHAR(100) NOT NULL,
    specializations TEXT[],
    years_experience INTEGER,
    hourly_rate DECIMAL(8, 2),
    bio TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI valuations table
CREATE TABLE IF NOT EXISTS ai_valuations (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    estimated_price DECIMAL(12, 2) NOT NULL,
    confidence_score DECIMAL(3, 2),
    valuation_factors JSONB, -- Store factors that influenced the valuation
    market_data JSONB, -- Store comparable properties data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI recommendations table (for home improvement suggestions)
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL,
    recommendation_text TEXT NOT NULL,
    estimated_cost DECIMAL(10, 2),
    estimated_value_increase DECIMAL(10, 2),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    uploader_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER,
    is_signed BOOLEAN DEFAULT FALSE,
    signature_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_seller_id ON properties(seller_id);
CREATE INDEX IF NOT EXISTS idx_properties_address_id ON properties(address_id);
CREATE INDEX IF NOT EXISTS idx_addresses_city ON addresses(city);
CREATE INDEX IF NOT EXISTS idx_addresses_state ON addresses(state);
CREATE INDEX IF NOT EXISTS idx_property_images_property_id ON property_images(property_id);
CREATE INDEX IF NOT EXISTS idx_property_images_is_primary ON property_images(is_primary);
CREATE INDEX IF NOT EXISTS idx_conversations_property_id ON conversations(property_id);
CREATE INDEX IF NOT EXISTS idx_conversations_buyer_id ON conversations(buyer_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_bookings_property_id ON bookings(property_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(scheduled_date);

-- Insert sample data for testing
INSERT INTO users (email, first_name, last_name, user_type, oauth_provider, oauth_id) VALUES
('agent@example.com', 'John', 'Agent', 'agent', 'google', 'google-123'),
('consumer@example.com', 'Jane', 'Consumer', 'consumer', 'google', 'google-456'),
('lawyer@example.com', 'Bob', 'Attorney', 'lawyer', 'google', 'google-789');

-- Insert sample addresses
INSERT INTO addresses (street_address, city, state, zip_code) VALUES
('123 Main Street', 'Springfield', 'IL', '62701'),
('456 Oak Avenue', 'Springfield', 'IL', '62702'),
('789 Pine Street', 'Springfield', 'IL', '62703'),
('321 Elm Drive', 'Springfield', 'IL', '62704'),
('555 Mansion Lane', 'Springfield', 'IL', '62705'),
('888 Factory Road', 'Springfield', 'IL', '62706');

-- Insert sample properties with address references
INSERT INTO properties (seller_id, address_id, title, description, property_type, price, bedrooms, bathrooms, square_feet, status) VALUES
(1, 1, 'Beautiful Family Home', 'Spacious 3-bedroom house in quiet neighborhood with updated kitchen and hardwood floors throughout', 'house', 450000.00, 3, 2, 2200, 'active'),
(1, 2, 'Modern Downtown Condo', 'Luxury 2-bedroom condo with city views, granite countertops, and balcony', 'condo', 275000.00, 2, 2, 1100, 'active'),
(1, 3, 'Charming Townhouse', 'End unit townhouse with private patio, 2-car garage, and finished basement', 'townhouse', 320000.00, 3, 2, 1800, 'active'),
(1, 4, 'Cozy Starter Home', 'Perfect first home with updated appliances and fenced backyard', 'house', 185000.00, 2, 1, 950, 'active'),
(1, 5, 'Executive Estate', 'Magnificent 5-bedroom home on 2 acres with pool and guest house', 'house', 750000.00, 5, 4, 4500, 'active'),
(1, 6, 'Urban Loft', 'Industrial-style loft in converted warehouse with exposed brick and high ceilings', 'apartment', 225000.00, 1, 1, 800, 'active');

-- Insert sample property images
INSERT INTO property_images (property_id, image_url, alt_text, is_primary, display_order) VALUES
(1, '/uploads/properties/1/main.jpg', 'Beautiful Family Home - Main View', TRUE, 0),
(1, '/uploads/properties/1/kitchen.jpg', 'Beautiful Family Home - Kitchen', FALSE, 1),
(2, '/uploads/properties/2/main.jpg', 'Modern Downtown Condo - Main View', TRUE, 0),
(2, '/uploads/properties/2/balcony.jpg', 'Modern Downtown Condo - Balcony View', FALSE, 1),
(3, '/uploads/properties/3/main.jpg', 'Charming Townhouse - Main View', TRUE, 0),
(4, '/uploads/properties/4/main.jpg', 'Cozy Starter Home - Main View', TRUE, 0),
(5, '/uploads/properties/5/main.jpg', 'Executive Estate - Main View', TRUE, 0),
(6, '/uploads/properties/6/main.jpg', 'Urban Loft - Main View', TRUE, 0);