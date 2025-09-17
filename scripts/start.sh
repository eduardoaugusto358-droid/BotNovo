#!/bin/bash

echo "🚀 Starting WhatsApp Bot Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in production
if [ "$NODE_ENV" = "production" ]; then
    print_status "Running in production mode"
    export ENVIRONMENT=production
else
    print_status "Running in development mode"
    export ENVIRONMENT=development
fi

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h ${DATABASE_HOST:-localhost} -p ${DATABASE_PORT:-5432} -U ${DATABASE_USER:-admin}; do
    print_warning "PostgreSQL is not ready yet. Waiting..."
    sleep 2
done

print_status "PostgreSQL is ready!"

# Run database migrations
print_status "Running database migrations..."
if alembic upgrade head; then
    print_status "Database migrations completed successfully"
else
    print_error "Database migrations failed"
    exit 1
fi

# Initialize database if needed
print_status "Checking if database initialization is needed..."
if python scripts/init_db.py; then
    print_status "Database initialization completed"
else
    print_warning "Database initialization had issues, but continuing..."
fi

# Start the application
print_status "Starting FastAPI application..."
print_status "API Documentation will be available at: http://localhost:8000/api/docs"
print_status "Main Application will be available at: http://localhost:8000"

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info