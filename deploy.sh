#!/bin/bash
# Deploy AI Footprints real data
# This script:
# 1. Runs the tracker to collect fresh data
# 2. Converts data to page format
# 3. Deploys to rakukit server

set -e

SCRIPT_DIR="$HOME/scripts/person-tracker"
REMOTE_SERVER="ubuntu@138.2.33.17"
REMOTE_PATH="/var/www/rakukit/apps/ai-footprints/app"

echo "🚀 Deploying AI Footprints real data..."

# Step 1: Run tracker
echo "📡 Step 1: Collecting news data..."
cd "$SCRIPT_DIR"
/usr/bin/python3 tracker.py

# Step 2: Convert to page format
echo "🔄 Step 2: Converting to page format..."
/usr/bin/python3 convert-to-page.py

# Step 3: Deploy to server
echo "📦 Step 3: Deploying to server..."
ssh "$REMOTE_SERVER" "mkdir -p $REMOTE_PATH/data"
scp "$SCRIPT_DIR/output/page-data.json" "$REMOTE_SERVER:$REMOTE_PATH/data/"

echo "✅ Deployment complete!"
echo "📊 Data file: $REMOTE_PATH/data/page-data.json"
echo ""
echo "⚠️  Note: The page JS needs to be updated to load from this JSON file."
echo "   See the AI Footprints page source for integration instructions."
