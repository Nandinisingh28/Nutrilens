#!/bin/bash

# NutriLens Development Environment - Start Script
# Usage: ./scripts/dev-up.sh

set -e

echo "🚀 Starting NutriLens development environment..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
fi

# Start Docker Compose
echo "🐳 Starting Docker containers..."
docker compose up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ NutriLens is running!"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   MySQL:    localhost:3306"
echo ""
echo "📝 To view logs: docker compose logs -f"
