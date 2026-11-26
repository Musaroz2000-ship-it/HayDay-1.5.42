#!/bin/sh
cd "$(dirname "$0")"

echo "[*] Configuring server to run on this device (127.0.0.1)..."
python3 setup_host.py 127.0.0.1

echo
echo "================================================"
echo "  SERVER STARTS NOW. Keep Termux OPEN while playing."
echo "  Tap Termux notification -> Acquire wakelock."
echo "  Press Ctrl+C to stop."
echo "================================================"
echo

exec python3 Main.py
