#!/bin/sh
cd "$(dirname "$0")"

echo "[*] Installing requirements..."
python3 -m pip install -q -r requirements.txt

echo "[*] Detecting LAN IP..."
python3 setup_host.py

echo
echo "================================================"
echo "  SERVER STARTS NOW. Keep this terminal OPEN."
echo "  Play Hay Day on your phone (same Wi-Fi)."
echo "  Press Ctrl+C to stop."
echo "================================================"
echo

exec python3 Main.py
