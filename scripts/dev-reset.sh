#!/bin/bash

# NutriLens Development Environment - Reset Script
# Usage: ./scripts/dev-reset.sh
# WARNING: This will delete all data in the database!

set -e

echo "⚠️  WARNING: This will delete all data in the database!"
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Reset cancelled."
    exit 1
fi

echo "🔄 Resetting NutriLens development environment..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Stop and remove containers, volumes
echo "🗑️  Removing containers and volumes..."
docker compose down -v

# Remove uploads
echo "🗑️  Cleaning uploads..."
rm -rf ./uploads/*

# Recreate .env if needed
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
fi

# Start fresh
echo "🚀 Starting fresh environment..."
docker compose up -d --build

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ NutriLens has been reset and restarted!"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   MySQL:    localhost:3306"
