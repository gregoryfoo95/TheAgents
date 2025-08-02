# Environment Variables Setup

This document explains how to set up environment variables for the TheAgents property marketplace application.

## Overview

The application consists of two main parts:
- **Backend**: FastAPI application with PostgreSQL and Redis
- **Frontend**: React application built with Vite

Each part requires its own set of environment variables.

## Backend Environment Variables

### Required Files
- Copy `backend/.env.sample` to `backend/.env`
- Modify the values according to your setup

### Key Variables

#### Database Configuration
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/property_marketplace
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/property_marketplace
```

#### Security
```env
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Redis
```env
REDIS_URL=redis://localhost:6379
```

#### CORS (Frontend URLs)
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### AI Features (Optional)
```env
OPENAI_API_KEY=your-openai-api-key-here
```

## Frontend Environment Variables

### Required Files
- Copy `frontend/.env.sample` to `frontend/.env`
- Modify the values according to your setup

### Key Variables

#### Backend API
```env
VITE_API_URL=http://localhost:8000
```

#### App Configuration
```env
VITE_APP_NAME=TheAgents
VITE_APP_VERSION=1.0.0
VITE_NODE_ENV=development
```

#### Feature Flags
```env
VITE_ENABLE_AI_FEATURES=true
VITE_ENABLE_CHAT=true
VITE_ENABLE_LAWYER_INTEGRATION=true
VITE_ENABLE_ANALYTICS=false
```

## Development Setup

### 1. Root Environment Setup (Docker)
```bash
# Copy the root environment template
cp .env.sample .env
# Edit .env file with your credentials (defaults work for development)
```

### 2. Backend Setup
```bash
cd backend
cp .env.sample .env
# Edit .env file with your database credentials
```

### 3. Frontend Setup
```bash
cd frontend
cp .env.sample .env
# Edit .env file if needed (defaults should work for development)
```

### 4. Docker Setup
The `docker-compose.yml` file uses environment variables from the root `.env` file for all service configuration.

### 5. Database Management (pgAdmin)
pgAdmin is included for visual database management:
- **URL**: http://localhost:5050
- **Email**: Set in root `.env` file (default: admin@theagents.com)
- **Password**: Set in root `.env` file (default: admin123)
- **See**: [PGADMIN_SETUP.md](./PGADMIN_SETUP.md) for detailed setup instructions

## Production Considerations

### Root Environment Variables (Docker)
- **POSTGRES_PASSWORD**: Use a strong, unique password
- **SECRET_KEY**: Generate a secure random key (minimum 32 characters)
- **PGADMIN_DEFAULT_PASSWORD**: Use a strong, unique password
- **PGADMIN_CONFIG_SERVER_MODE**: Set to `True` for multi-user access

### Backend Production Variables
- **SECRET_KEY**: Generate a secure random key (minimum 32 characters)
- **DATABASE_URL**: Use production database credentials
- **DEBUG**: Set to `false`
- **ALLOWED_ORIGINS**: Set to your production frontend URL
- **OPENAI_API_KEY**: Add your production OpenAI API key for AI features

### Frontend Production Variables
- **VITE_API_URL**: Set to your production backend URL
- **VITE_NODE_ENV**: Set to `production`
- **VITE_DEBUG_MODE**: Set to `false`

## Optional Integrations

### Email Service
Add to backend `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Stripe Payments
Add to backend `.env`:
```env
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

Add to frontend `.env`:
```env
VITE_STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
```

### Google Maps
Add to frontend `.env`:
```env
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### AWS S3 Storage
Add to backend `.env`:
```env
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
```

## Security Notes

1. **Never commit `.env` files to version control**
2. **Always use `.env.sample` files as templates**
3. **Generate strong, unique secret keys for production**
4. **Regularly rotate API keys and secrets**
5. **Use environment-specific configurations**

## Troubleshooting

### Common Issues

1. **Backend can't connect to database**: Check `DATABASE_URL` format and credentials
2. **Frontend can't reach backend**: Verify `VITE_API_URL` matches backend port
3. **CORS errors**: Ensure frontend URL is in `ALLOWED_ORIGINS`
4. **AI features not working**: Verify `OPENAI_API_KEY` is set and valid

### Environment Variable Loading

- **Backend**: Uses `pydantic-settings` to load from `.env` file
- **Frontend**: Uses Vite's built-in environment variable loading
- **Docker**: Environment variables are set in `docker-compose.yml`