#!/bin/bash
set -e

echo "Starting META Urls Manager..."

echo "Waiting for MongoDB to be ready..."
until python -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio, os

async def check():
    client = AsyncIOMotorClient(os.environ.get('MONGO__HOST', 'db'), int(os.environ.get('MONGO__PORT', 27017)))
    await client.admin.command('ping')

asyncio.run(check())
" 2>/dev/null; do
    echo "MongoDB is not ready yet. Retrying in 2s..."
    sleep 2
done
echo "MongoDB is ready!"

# Execute the main command (passed as CMD in Dockerfile or command in docker-compose)
exec "$@"
