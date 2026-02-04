#!/bin/bash

# NutriLens Development Environment - Stop Script
# Usage: ./scripts/dev-down.sh

set -e

echo "🛑 Stopping NutriLens development environment..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Stop Docker Compose
docker compose down

echo "✅ NutriLens has been stopped."
