# Database Setup - TheAgents Property Marketplace

This guide covers the complete database setup for the TheAgents property marketplace application.

## Overview

Your database stack includes:
- **PostgreSQL 15**: Main database for application data
- **Redis 7**: Caching and session storage  
- **pgAdmin 4**: Web-based database administration tool

## Quick Start

### 1. Setup Environment Variables
```bash
# Copy the root environment template (required for Docker Compose)
cp .env.sample .env
# Edit .env file if needed (defaults work for development)
```

### 2. Start All Services
```bash
# Option 1: Use the convenience script
./start-services.sh

# Option 2: Use Docker Compose directly
docker-compose up -d
```

### 3. Access pgAdmin
- **URL**: http://localhost:5050
- **Login**: Credentials from root `.env` file (default: admin@theagents.com / admin123)
- **Setup**: See [PGADMIN_SETUP.md](./PGADMIN_SETUP.md)

### 4. Database Connection Details
```
Host: localhost (or 'postgres' from within Docker network)
Port: 5432
Database: property_marketplace
Username: postgres
Password: postgres123
```

## Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    user_type VARCHAR(20) NOT NULL, -- 'buyer', 'seller', 'lawyer'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Properties Table  
```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    property_type VARCHAR(50) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    bedrooms INTEGER,
    bathrooms INTEGER,
    square_feet INTEGER,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    images TEXT[], -- Array of image URLs
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Relationships

- **One-to-Many**: User → Properties (one user can own many properties)
- **One-to-Many**: Property → Bookings (one property can have many bookings)
- **Many-to-Many**: Users ↔ Conversations (through conversations table)
- **One-to-One**: User → LawyerProfile (lawyers have extended profiles)

## Sample Data

The database includes sample data for testing:

### Sample Users
- **Buyer**: John Doe (john.doe@example.com)
- **Seller**: Jane Smith (jane.smith@example.com)  
- **Lawyer**: Bob Johnson (bob.johnson@example.com)

### Sample Properties
- 6 diverse properties with different types, prices, and locations
- Properties are owned by the sample seller
- Include realistic details (bedrooms, bathrooms, square footage)

## Common Database Operations

### View All Tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### Check Relationships
```sql
-- Properties with their sellers
SELECT p.title, p.price, u.first_name || ' ' || u.last_name as seller
FROM properties p
JOIN users u ON p.seller_id = u.id;
```

### User Statistics
```sql
-- Count users by type
SELECT user_type, COUNT(*) as count
FROM users
GROUP BY user_type;
```

### Property Statistics
```sql
-- Average price by property type
SELECT property_type, 
       ROUND(AVG(price), 2) as avg_price,
       COUNT(*) as count
FROM properties
GROUP BY property_type;
```

## Development Workflow

### Making Schema Changes

1. **Modify SQLAlchemy Models** (in `/backend/models/`)
2. **Update Pydantic Schemas** (in `/backend/schemas/`)
3. **Run Database Migrations** (if using Alembic)
4. **Refresh pgAdmin** to see changes
5. **Test with Sample Data**

### Testing Database Operations

```bash
# Connect to database directly
docker exec -it the_agents_db psql -U postgres -d property_marketplace

# View logs
docker logs the_agents_db

# Backup database
docker exec the_agents_db pg_dump -U postgres property_marketplace > backup.sql

# Restore database
docker exec -i the_agents_db psql -U postgres property_marketplace < backup.sql
```

## Environment Variables

### Root Environment File (.env)
```env
# PostgreSQL Database
POSTGRES_DB=property_marketplace
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Backend Services
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/property_marketplace
REDIS_URL=redis://redis:6379
SECRET_KEY=dev-secret-key-change-in-production

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@theagents.com
PGADMIN_DEFAULT_PASSWORD=admin123

# Frontend
VITE_API_URL=http://localhost:8000
```

### Backend Environment File (backend/.env)
```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/property_marketplace
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/property_marketplace
REDIS_URL=redis://localhost:6379
```

## Troubleshooting

### Database Won't Start
```bash
# Check if port 5432 is in use
lsof -i :5432

# View PostgreSQL logs
docker logs the_agents_db

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d postgres
```

### pgAdmin Connection Issues
```bash
# Restart pgAdmin
docker-compose restart pgadmin

# Check pgAdmin logs
docker logs the_agents_pgadmin

# Verify network connectivity
docker exec the_agents_pgadmin ping postgres
```

### Performance Issues
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- View slow queries (if query logging enabled)
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

## Security Considerations

### Development
- Simple passwords for easy local development
- No SSL/TLS encryption
- Open access within Docker network

### Production
- Change all default passwords
- Enable SSL/TLS for PostgreSQL
- Restrict network access
- Use connection pooling
- Regular backups and monitoring

## Backup Strategy

### Manual Backup
```bash
# Full database backup
docker exec the_agents_db pg_dump -U postgres property_marketplace > backup_$(date +%Y%m%d_%H%M%S).sql

# Schema only
docker exec the_agents_db pg_dump -U postgres -s property_marketplace > schema_backup.sql

# Data only
docker exec the_agents_db pg_dump -U postgres -a property_marketplace > data_backup.sql
```

### Automated Backup (Production)
Consider setting up automated backups using:
- pg_dump with cron jobs
- PostgreSQL streaming replication
- Cloud provider backup services (AWS RDS, Google Cloud SQL)

## Monitoring

### Health Checks
```bash
# PostgreSQL health
docker exec the_agents_db pg_isready -U postgres

# Redis health  
docker exec the_agents_redis redis-cli ping

# Check all services
docker-compose ps
```

### Database Metrics
- Connection count
- Query performance
- Disk usage
- Memory usage
- Lock contention

For detailed pgAdmin setup instructions, see [PGADMIN_SETUP.md](./PGADMIN_SETUP.md).
For environment configuration, see [ENV_SETUP.md](./ENV_SETUP.md).