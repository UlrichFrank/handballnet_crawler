#!/bin/bash
# Load game data from data branch locally
# Useful before running scraper.py to get existing data
# Usage: ./load_data_branch.sh

echo "📥 Loading game data from data branch..."
echo ""

# Fetch the data branch
git fetch origin data

# Create a temporary directory
mkdir -p _data_temp

# Checkout data from the data branch
git checkout origin/data -- frontend/public/data 2>/dev/null || {
    echo "⚠️  Could not checkout data from data branch (may be first run)"
    exit 0
}

echo "✅ Game data loaded from data branch"
echo ""
echo "You can now run the scraper:"
echo "  python scraper.py"
echo ""
echo "After scraping, sync data back to data branch:"
echo "  ./sync_data_branch.sh"
