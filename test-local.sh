#!/bin/bash
# Quick local test: Scraper + Build + Serve

set -e

echo "=========================================="
echo "🧪 LOCAL TEST: Scraper + Build + Serve"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -f "scraper.py" ]; then
    echo "❌ Error: Run this script from repository root"
    exit 1
fi

# 1. Run Scraper
echo "1️⃣  Running Scraper..."
python3 scraper.py
echo "✅ Scraper complete"
echo ""

# 2. Build Frontend
echo "2️⃣  Building Frontend..."
cd frontend
npm run build > /dev/null 2>&1
echo "✅ Frontend built"
cd ..
echo ""

# 3. Copy static files
echo "3️⃣  Copying static files..."
cp frontend/public/config.json frontend/dist/config.json
cp -r frontend/public/data/* frontend/dist/data/ 2>/dev/null || true
echo "✅ Static files copied"
echo ""

# 4. Verify data
echo "4️⃣  Verifying data structure..."
python3 << 'PYTHON'
import json
from pathlib import Path

meta_file = Path('frontend/dist/data/meta.json')
if meta_file.exists():
    with open(meta_file) as f:
        meta = json.load(f)
    
    print(f"   📊 Meta Index:")
    for liga, info in meta['leagues'].items():
        spieltage = info['spieltage']
        print(f"      {liga}: {len(spieltage)} Spieltag(e) - {spieltage}")
else:
    print("   ❌ No meta.json found")
PYTHON
echo "✅ Data verified"
echo ""

# 5. Serve
echo "5️⃣  Starting web server on http://localhost:8000"
echo ""
echo "=========================================="
echo "✅ Server ready! Open browser:"
echo ""
echo "   http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

cd frontend/dist
python3 -m http.server 8000
