#!/bin/bash

# Snapshot Environment Configuration Script
# Use this to set up the backend with a rich data state for UI testing/viewing.

echo "==========================================="
echo "   Nexus Root - Snapshot Setup Script"
echo "==========================================="

# 1. Install Dependencies
echo "[1/3] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "      Dependencies installed."
    else
        echo "      Warning: dependency installation failed or partial."
    fi
else
    echo "      requirements.txt not found, skipping."
fi

# 2. Create Snapshot Data
echo "[2/3] Seeding database with snapshot data..."
python3 scripts/create_snapshot.py
if [ $? -eq 0 ]; then
    echo "      Snapshot data created successfully."
else
    echo "      Error creating snapshot data."
    exit 1
fi

# 3. Instructions
echo "[3/3] Setup Complete."
echo ""
echo "To view the UI with this snapshot:"
echo "1. Start the server:"
echo "   python3 main.py server"
echo ""
echo "2. Connect with Client:"
echo "   - Web: Open http://localhost:8080"
echo "   - Android: Run the app and login as 'snapshot_user'"
echo "     (No password verification implemented for local dev usually, or check logs)"
echo ""
echo "==========================================="
