# Property Marketplace - Agent-Free Real Estate Platform

A comprehensive property marketplace application that enables buyers and sellers to connect directly without traditional real estate agents. The platform features AI-powered property valuations, smart improvement recommendations, integrated legal support, and seamless communication tools.

## 🏗️ Architecture Overview

The application follows a clean architecture pattern with clear separation of concerns:

### Backend Architecture

```
backend/
├── core/                   # Core configuration and shared utilities
│   ├── config.py          # Application settings with Pydantic
│   ├── database.py        # Database setup and session management
│   └── redis.py           # Redis client and caching utilities
├── models/                # Domain models split by entity
│   ├── user.py           # User and authentication models
│   ├── property.py       # Property and feature models
│   ├── conversation.py   # Chat and messaging models
│   ├── booking.py        # Viewing booking models
│   ├── lawyer.py         # Lawyer profile models
│   ├── ai.py            # AI valuation and recommendation models
│   └── document.py       # Document sharing models
├── schemas/              # Pydantic schemas for validation
│   ├── base.py          # Base schemas and generic types
│   ├── user.py          # User-related schemas
│   ├── property.py      # Property-related schemas
│   └── ...              # Other domain schemas
├── repositories/         # Data access layer
│   ├── base.py          # Base repository with common operations
│   ├── user.py          # User data access
│   ├── property.py      # Property data access
│   └── ...              # Other repositories
├── services/            # Business logic layer
│   ├── user.py          # User business logic
│   ├── property.py      # Property business logic
│   ├── ai.py           # AI services
│   └── ...              # Other services
├── controllers/         # HTTP request/response handling
│   ├── user.py          # User endpoints
│   ├── property.py      # Property endpoints
│   └── ...              # Other controllers
├── middleware/          # Custom middleware
│   ├── auth.py          # Authentication middleware
│   └── validation.py    # Input validation middleware
└── main.py             # FastAPI application setup
```

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   ├── pages/           # Page components
│   ├── contexts/        # React contexts (Auth, etc.)
│   ├── services/        # API client and services
│   ├── types/           # TypeScript type definitions
│   └── App.tsx          # Main application component
├── public/              # Static assets
└── package.json         # Dependencies and scripts
```

## 🚀 Features

### Core Features
- **Direct Property Listings**: Sellers can list properties without agent fees
- **Advanced Search & Filtering**: Buyers can find properties with detailed filters
- **Real-time Messaging**: Direct communication between buyers, sellers, and lawyers
- **Booking System**: Schedule property viewings with conflict resolution
- **Document Sharing**: Secure legal document exchange and management

### AI-Powered Features
- **Property Valuation**: AI-driven property price estimation using market data
- **Improvement Recommendations**: Vision-based suggestions for home improvements
- **Market Analysis**: Real-time market trends and comparable property analysis

### Legal Integration
- **Lawyer Directory**: Find and connect with verified property lawyers
- **Document Management**: Handle legal paperwork digitally
- **Transaction Support**: End-to-end legal support for property transactions

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database for data persistence
- **Redis**: In-memory caching and session storage
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Celery**: Distributed task queue for background jobs
- **LangChain**: AI framework for property analysis
- **WebSockets**: Real-time communication

### Frontend
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and state management
- **Socket.io**: Real-time client-side communication
- **React Router**: Client-side routing

### Infrastructure
- **Docker**: Containerization for all services
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving (production)

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd property-marketplace
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Redis: http://localhost:6379
   - PostgreSQL: http://localhost:5432

### Local Development

#### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the database:**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend:**
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

## 🏛️ Database Schema

### Core Entities

- **Users**: Buyers, sellers, and lawyers with role-based access
- **Properties**: Real estate listings with features and images
- **Conversations**: Chat threads between users
- **Messages**: Individual chat messages with file attachments
- **Bookings**: Property viewing appointments
- **Lawyer Profiles**: Professional information for legal services
- **AI Valuations**: AI-generated property valuations
- **AI Recommendations**: Home improvement suggestions
- **Documents**: Legal and property documents

### Key Relationships

- Users can have multiple properties (sellers)
- Properties can have multiple conversations
- Conversations contain multiple messages
- Users can have multiple bookings
- Properties can have multiple AI valuations and recommendations

## 🔐 Authentication & Security

- **JWT-based authentication** with secure token handling
- **Role-based access control** (buyer, seller, lawyer)
- **Password hashing** using bcrypt
- **Input validation** with Pydantic schemas
- **SQL injection protection** via SQLAlchemy ORM
- **CORS configuration** for secure cross-origin requests

## 📡 API Documentation

The API is fully documented using OpenAPI/Swagger. Access the interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login
- `GET /api/users/me` - Get current user

#### Properties
- `GET /api/properties/` - List properties with filters
- `POST /api/properties/` - Create property (sellers only)
- `GET /api/properties/{id}` - Get property details
- `PUT /api/properties/{id}` - Update property
- `POST /api/properties/{id}/images` - Upload property images

#### AI Services
- `POST /api/ai/valuate/{property_id}` - Get AI property valuation
- `POST /api/ai/recommendations/{property_id}` - Get improvement recommendations

#### Chat & Messaging
- `GET /api/chat/conversations/` - List user conversations
- `POST /api/chat/messages/` - Send message
- `WebSocket /api/chat/ws/{user_id}` - Real-time messaging

## 🤖 AI Integration

### Property Valuation Agent
- **Market Analysis**: Scrapes web data for comparable properties
- **Price Estimation**: ML models for accurate valuations
- **Confidence Scoring**: Reliability metrics for estimates

### Home Improvement Recommendations
- **Image Analysis**: Computer vision for property assessment
- **ROI Calculations**: Cost vs. value increase analysis
- **Priority Ranking**: Recommendations sorted by impact

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### E2E Testing
```bash
npm run test:e2e
```

## 📈 Performance & Scaling

### Caching Strategy
- **Redis caching** for frequently accessed data
- **Property listings** cached for 5 minutes
- **AI valuations** cached for 1 hour
- **User sessions** stored in Redis

### Database Optimization
- **Indexed queries** on frequently searched fields
- **Eager loading** for related entities
- **Pagination** for large datasets
- **Connection pooling** for database efficiency

## 🚀 Deployment

### Production Deployment

1. **Set up environment variables:**
   ```bash
   cp .env.example .env.production
   # Configure production settings
   ```

2. **Build and deploy:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables

Key environment variables to configure:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Security
SECRET_KEY=your-super-secret-key
DEBUG=false

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Redis
REDIS_URL=redis://host:port

# File Storage
MAX_FILE_SIZE=10485760  # 10MB
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, email support@propertymarketplace.com or join our [Discord community](https://discord.gg/propertymarketplace).

## 🗺️ Roadmap

- [ ] Mobile app development (React Native)
- [ ] Advanced AI features (property matching)
- [ ] Integration with MLS systems
- [ ] Blockchain-based smart contracts
- [ ] Virtual property tours
- [ ] Mortgage calculator integration
- [ ] Insurance marketplace
- [ ] Property investment analytics