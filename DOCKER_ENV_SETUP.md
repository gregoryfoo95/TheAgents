# Docker Environment Configuration

This document explains the multi-layered environment variable setup for TheAgents property marketplace.

## Overview

The project uses a **three-tier environment configuration**:

1. **Root `.env`** - Docker Compose configuration
2. **Backend `.env`** - FastAPI application configuration  
3. **Frontend `.env`** - React/Vite application configuration

## Environment File Structure

```
TheAgents/
├── .env                    # Docker Compose variables
├── .env.sample             # Docker Compose template
├── backend/
│   ├── .env                # Backend app variables
│   └── .env.sample         # Backend app template
└── frontend/
    ├── .env                # Frontend app variables
    └── .env.sample         # Frontend app template
```

## 1. Root Environment (.env)

**Purpose**: Configures Docker Compose services (PostgreSQL, Redis, pgAdmin, etc.)

**Key Variables**:
```env
# Database
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

## 2. Backend Environment (backend/.env)

**Purpose**: Configures FastAPI application settings

**Key Variables**:
```env
# Database (for non-Docker development)
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/property_marketplace
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/property_marketplace

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
OPENAI_API_KEY=
```

## 3. Frontend Environment (frontend/.env)

**Purpose**: Configures React/Vite application settings

**Key Variables**:
```env
# API Configuration
VITE_API_URL=http://localhost:8000

# App Configuration
VITE_APP_NAME=TheAgents
VITE_ENABLE_AI_FEATURES=true

# Debug Settings
VITE_DEBUG_MODE=true
```

## Setup Instructions

### Quick Setup (Development)
```bash
# 1. Copy all environment templates
cp .env.sample .env
cp backend/.env.sample backend/.env  
cp frontend/.env.sample frontend/.env

# 2. Start services
./start-services.sh
```

### Manual Setup

#### 1. Root Environment
```bash
cp .env.sample .env
# Edit .env with your Docker configuration
```

#### 2. Backend Environment  
```bash
cd backend
cp .env.sample .env
# Edit backend/.env with your FastAPI configuration
```

#### 3. Frontend Environment
```bash
cd frontend  
cp .env.sample .env
# Edit frontend/.env with your React configuration
```

## Environment Variable Flow

### Docker Compose → Services
```yaml
# docker-compose.yml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # From root .env

  backend:
    environment:
      DATABASE_URL: ${DATABASE_URL}            # From root .env
      SECRET_KEY: ${SECRET_KEY}                # From root .env
```

### Backend Application
```python
# backend/utilities/config.py
class Settings(BaseSettings):
    database_url: str = "postgresql://..."  # From backend/.env
    secret_key: str = "default-key"         # From backend/.env
    
    class Config:
        env_file = ".env"  # Loads backend/.env
```

### Frontend Application
```typescript
// frontend/src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL  // From frontend/.env
```

## Security Considerations

### Development
- Simple passwords for local development
- Debug modes enabled
- All services accessible locally

### Production
- **Root .env**: Strong database passwords, secure pgAdmin access
- **Backend .env**: Production database URLs, strong SECRET_KEY
- **Frontend .env**: Production API URLs, debug modes disabled

## Common Issues

### Environment Not Loading
```bash
# Check if .env files exist
ls -la .env
ls -la backend/.env  
ls -la frontend/.env

# Validate Docker Compose config
docker-compose config
```

### Variable Conflicts
1. **Docker vs Local**: Root `.env` for Docker, backend/frontend `.env` for local development
2. **Precedence**: Local environment variables override `.env` files
3. **Syntax**: Use `${VAR}` in docker-compose.yml, no spaces around `=`

### Password Mismatches
```bash
# Ensure DATABASE_URL in root .env matches backend expectations
# Root: postgresql://postgres:PASSWORD@postgres:5432/db
# Backend: postgresql://postgres:PASSWORD@localhost:5432/db
```

## Best Practices

### 1. Use Templates
- Always maintain `.env.sample` files
- Include comments explaining each variable
- Provide secure defaults for production

### 2. Layer Separation
- **Root**: Infrastructure (databases, networks)
- **Backend**: Application logic (APIs, features)  
- **Frontend**: UI behavior (endpoints, features)

### 3. Security
- Never commit actual `.env` files
- Use strong passwords in production
- Rotate secrets regularly
- Use different credentials per environment

### 4. Documentation
- Document all environment variables
- Explain the purpose of each layer
- Provide setup examples for different scenarios

## Troubleshooting Commands

```bash
# View resolved Docker Compose configuration
docker-compose config

# Check environment variable loading in containers
docker exec the_agents_backend env | grep DATABASE
docker exec the_agents_frontend env | grep VITE

# Test backend configuration
docker exec the_agents_backend python -c "from utilities.config import get_settings; print(get_settings().database_url)"

# Restart with fresh environment
docker-compose down
docker-compose up -d
```

This multi-layered approach provides flexibility for different deployment scenarios while maintaining security and clarity.