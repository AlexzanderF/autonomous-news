#!/bin/bash

# Deployment script for autonomous-news
# This script updates the codebase and rebuilds/restarts Docker containers

set -e  # Exit on any error

echo "🔄 Fetching latest changes..."
git fetch

echo "📥 Pulling with rebase..."
git pull --rebase

echo "🏗️  Building and starting containers..."
docker compose up -d --build celery-worker nextjs fastapi

echo "🔁 Restarting services..."
docker compose restart nextjs fastapi nginx celery-worker

echo "✅ Deployment complete!"
