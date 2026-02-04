#!/bin/bash
# Sync game data to data branch after scraping
# Usage: ./sync_data_branch.sh

set -e

echo "🔄 Syncing game data to data branch..."
echo ""

# Configure git
git config user.name "Local Scraper"
git config user.email "scraper@local"

# Check if there are data changes
if [ -z "$(git status --porcelain frontend/public/data/)" ]; then
    echo "✅ No new game data to commit"
    exit 0
fi

echo "📝 Committing game data changes..."
git add frontend/public/data/
git commit -m "chore: Update game data from local scraper [skip ci]"

echo "📤 Pushing to data branch..."
git push origin HEAD:data

echo ""
echo "✅ Game data committed and pushed to data branch"
echo ""
echo "Next steps for local development:"
echo "  1. Keep working on main branch (data is safely stored on data branch)"
echo "  2. On next scraper run, data will be auto-loaded from data branch"
