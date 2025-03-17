#!/bin/bash

# Exit on error
set -e

echo "=== Preparing Encompliance Application for Production ==="

# 1. Clean up test users and data
echo "=== Cleaning up test users and data ==="
cd encompliance-backend
source venv/bin/activate
python cleanup_users.py --confirm --all
deactivate
cd ..

# 2. Create database migration for user settings
echo "=== Creating database migration for user settings ==="
cd encompliance-backend
source venv/bin/activate
python create_migration.py
deactivate
cd ..

# 3. Build Docker images
echo "=== Building Docker images ==="
docker compose build

# 4. Start the application in detached mode
echo "=== Starting the application ==="
docker compose up -d

echo "=== Application is now running in production mode ==="
echo "Access the application at http://localhost"
echo "To stop the application, run: docker compose down"
echo "To view logs, run: docker compose logs -f" 