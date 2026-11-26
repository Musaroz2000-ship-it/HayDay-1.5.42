#!/bin/sh
cd "$(dirname "$0")"

echo "[*] Configuring server to run on this device (127.0.0.1)..."
python3 setup_host.py 127.0.0.1

echo
echo "================================================"
echo "  SERVER STARTS NOW. Keep iSH OPEN while playing."
echo "  To switch back: swipe right on screen edge."
echo "  Press Ctrl+C (type) to stop."
echo "================================================"
echo

exec python3 Main.py
