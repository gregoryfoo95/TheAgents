# pgAdmin Setup Guide

This guide will help you set up and use pgAdmin to visually manage your PostgreSQL database for TheAgents property marketplace.

## Overview

pgAdmin is a web-based PostgreSQL administration tool that provides a graphical interface to:
- View and manage database tables
- Run SQL queries
- Monitor database performance
- Manage users and permissions
- Import/export data

## Quick Start

### 1. Start the Services
```bash
# Start all services including pgAdmin
docker-compose up -d

# Or start pgAdmin specifically
docker-compose up -d pgadmin
```

### 2. Access pgAdmin
- **URL**: http://localhost:5050
- **Email**: admin@theagents.com
- **Password**: admin123

### 3. Connect to PostgreSQL Database

#### First Time Setup:
1. **Login to pgAdmin** using the credentials above
2. **Add New Server** (right-click "Servers" → "Register" → "Server...")

#### Server Configuration:
**General Tab:**
- **Name**: TheAgents Database (or any name you prefer)

**Connection Tab:**
- **Host name/address**: `postgres` (Docker service name)
- **Port**: `5432`
- **Maintenance database**: `property_marketplace`
- **Username**: `postgres`
- **Password**: `postgres123`

**Advanced Tab (Optional):**
- **DB restriction**: `property_marketplace` (to only show this database)

#### Save and Connect:
- Click **Save** to connect to the database

## Exploring Your Database

Once connected, you can explore:

### Database Structure
```
TheAgents Database
└── property_marketplace
    ├── Schemas
    │   └── public
    │       ├── Tables
    │       │   ├── users
    │       │   ├── properties
    │       │   ├── bookings
    │       │   ├── conversations
    │       │   ├── messages
    │       │   └── lawyer_profiles
    │       └── Views
    └── ...
```

### Viewing Tables
1. **Navigate**: Servers → TheAgents Database → Databases → property_marketplace → Schemas → public → Tables
2. **Right-click** any table → "View/Edit Data" → "All Rows"
3. **See table structure**: Right-click table → "Properties" → "Columns"

### Common Tasks

#### View Sample Data
```sql
-- View all users
SELECT * FROM users LIMIT 10;

-- View properties with seller information
SELECT p.title, p.price, u.first_name, u.last_name 
FROM properties p 
JOIN users u ON p.seller_id = u.id;

-- View recent bookings
SELECT * FROM bookings 
ORDER BY created_at DESC 
LIMIT 10;
```

#### Check Relationships
```sql
-- See properties with their sellers
SELECT 
    p.id,
    p.title,
    p.price,
    u.first_name || ' ' || u.last_name as seller_name
FROM properties p
LEFT JOIN users u ON p.seller_id = u.id;

-- Count properties per user
SELECT 
    u.first_name || ' ' || u.last_name as user_name,
    COUNT(p.id) as property_count
FROM users u
LEFT JOIN properties p ON u.id = p.seller_id
WHERE u.user_type = 'seller'
GROUP BY u.id, u.first_name, u.last_name;
```

## Useful pgAdmin Features

### 1. Query Tool
- **Access**: Tools → Query Tool
- **Use**: Write and execute custom SQL queries
- **Shortcut**: F5 to execute query

### 2. ERD (Entity Relationship Diagram)
- **Access**: Right-click database → "ERD For Database"
- **Use**: Visual representation of table relationships
- **Features**: Drag tables around, see foreign key connections

### 3. Data Import/Export
- **Access**: Right-click table → "Import/Export Data"
- **Formats**: CSV, text files
- **Use**: Bulk data operations

### 4. Table Designer
- **Access**: Right-click table → "Properties"
- **Use**: Modify table structure, add columns, constraints

### 5. Monitoring
- **Access**: Dashboard tab when connected
- **Use**: See database activity, connections, performance

## Troubleshooting

### Cannot Connect to Database
1. **Check Docker containers**:
   ```bash
   docker-compose ps
   ```
   Ensure `postgres` and `pgadmin` containers are running

2. **Check network connectivity**:
   ```bash
   docker network ls
   docker inspect property_network
   ```

3. **Verify PostgreSQL is ready**:
   ```bash
   docker logs the_agents_db
   ```
   Look for "database system is ready to accept connections"

### pgAdmin Shows Empty Database
1. **Check database name**: Ensure you're connected to `property_marketplace`
2. **Run database migrations**: Ensure FastAPI has created tables
3. **Check init.sql**: Verify the init script ran successfully

### Permission Denied Errors
1. **Check credentials**: Verify postgres username/password
2. **Database exists**: Ensure `property_marketplace` database was created
3. **User permissions**: Verify postgres user has access

## Docker Commands

### View Logs
```bash
# pgAdmin logs
docker logs the_agents_pgadmin

# PostgreSQL logs  
docker logs the_agents_db

# All services
docker-compose logs
```

### Restart Services
```bash
# Restart pgAdmin only
docker-compose restart pgadmin

# Restart database only
docker-compose restart postgres

# Restart all services
docker-compose restart
```

### Reset pgAdmin Data
```bash
# Stop services
docker-compose down

# Remove pgAdmin volume (loses settings)
docker volume rm theagents_pgadmin_data

# Start again (will recreate)
docker-compose up -d
```

## Security Notes

### Development vs Production

**Development (Current Setup):**
- Simple credentials for easy access
- No SSL/TLS encryption
- Server mode disabled (single user)

**Production Recommendations:**
- Strong, unique passwords
- Enable SSL/TLS
- Configure server mode for multi-user access
- Use environment variables for credentials
- Restrict network access

### Changing Credentials
1. **Update docker-compose.yml**:
   ```yaml
   environment:
     PGADMIN_DEFAULT_EMAIL: your-email@domain.com
     PGADMIN_DEFAULT_PASSWORD: your-secure-password
   ```

2. **Restart container**:
   ```bash
   docker-compose restart pgadmin
   ```

## Advanced Features

### Custom Dashboards
- Create custom graphs and charts
- Monitor specific metrics
- Set up alerts

### Backup/Restore
- **Backup**: Right-click database → "Backup..."
- **Restore**: Right-click database → "Restore..."
- **Formats**: Custom, tar, plain SQL

### User Management
- Create additional database users
- Set permissions and roles
- Manage access control

## Integration with Development

### During Development
1. **Watch live changes**: Refresh pgAdmin after running migrations
2. **Debug queries**: Use Query Tool to test SQL before adding to code
3. **Inspect data**: Verify API operations created expected data
4. **Performance**: Use EXPLAIN to analyze slow queries

### Sample Development Workflow
1. **Make model changes** in FastAPI
2. **Run migrations** (if using Alembic)
3. **Refresh pgAdmin** to see new tables/columns
4. **Test in pgAdmin** before writing application code
5. **Monitor data** as you test your API endpoints

This setup gives you full visual control over your PostgreSQL database, making development and debugging much easier!