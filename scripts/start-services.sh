#!/bin/bash

# TheAgents - Start All Services
# This script starts all services including PostgreSQL, Redis, pgAdmin, Backend, and Frontend

echo "🚀 Starting TheAgents Property Marketplace Services..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start all services
echo "📦 Starting all services with Docker Compose..."
docker-compose up --build -d

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   pgAdmin:   http://localhost:5050"
echo "   Redis:     localhost:6379"
echo "   PostgreSQL: localhost:5432"
echo ""
echo "🔑 pgAdmin Credentials:"
echo "   Email:     admin@theagents.com"
echo "   Password:  admin123"
echo ""
echo "📖 For pgAdmin setup instructions, see: PGADMIN_SETUP.md"
echo "📖 For environment setup, see: ENV_SETUP.md"
echo ""
echo "🛑 To stop all services: docker-compose down"
echo "🔄 To restart services: docker-compose restart"
echo "📋 To view logs: docker-compose logs"