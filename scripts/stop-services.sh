#!/bin/bash

# TheAgents - Stop All Services
# This script stops all running Docker services

echo "🛑 Stopping TheAgents Property Marketplace Services..."
echo ""

# Stop all services
docker-compose down

echo ""
echo "📊 Remaining containers:"
docker-compose ps

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "💡 Tips:"
echo "   🚀 To start again: ./start-services.sh"
echo "   🗑️  To remove all data: docker-compose down -v"
echo "   🔄 To restart: docker-compose restart"