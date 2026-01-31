#!/usr/bin/env bash
APP=$PWD/pihole_disable.py

echo -e "\n======================"
echo "=== PIHOLE_DISABLE ==="
echo "======================"

echo "Activating Python environment"
source .venv/bin/activate
echo "Starting script"
python "$APP" > .pihole_disable.log 2> .pihole_disable.err