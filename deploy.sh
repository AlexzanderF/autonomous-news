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

echo "⏳ Waiting for containers to be ready..."
sleep 10  # Give containers time to start up

echo "🔁 Restarting nginx to pick up fresh upstreams..."
docker compose restart nginx

echo "✅ Deployment complete!"
