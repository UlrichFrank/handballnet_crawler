#!/bin/bash

# Setup script for Handball Web Application
# Kopiert Daten vom Output-Ordner zum Frontend und startet Dev Server

set -e  # Exit on error

echo "🏐 Handball Web App - Setup Script"
echo "===================================="
echo ""

# Check if files exist
if [ ! -f "config/config.json" ]; then
    echo "❌ Error: config/config.json nicht gefunden"
    exit 1
fi

if [ ! -f "output/spiele_c_jugend.json" ] && [ ! -f "output/spiele_d_jugend.json" ]; then
    echo "⚠️  Warnung: Keine Spieldaten-JSON Dateien in output/ gefunden"
    echo "   Führe zuerst aus: python scraper.py && python generate_excel_report.py"
fi

# Create directories
echo "📁 Erstelle Verzeichnisse..."
mkdir -p frontend/public/data

# Copy files
echo "📋 Kopiere Daten..."
cp config/config.json frontend/public/config.json
cp output/spiele_*.json frontend/public/data/ 2>/dev/null || echo "⚠️  Keine spiele_*.json Dateien gefunden"

echo "✅ Daten kopiert"
echo ""

# Install dependencies (if needed)
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installiere Dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✨ Setup abgeschlossen!"
echo ""
echo "🚀 Starte Development Server..."
echo "   → http://localhost:5173/handball"
echo ""
echo "Zum Beenden: Drücke Ctrl+C"
echo ""

cd frontend
npm run dev
