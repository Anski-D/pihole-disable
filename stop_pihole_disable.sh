#!/usr/bin/env bash
APP=$PWD/pihole_disable.py

echo -e "\n======================"
echo "=== PIHOLE_DISABLE ==="
echo "======================"

echo "Creating STOP file"
touch STOP
echo "Waiting for Python script to stop..."
while [ -z $(pgrep -f "$APP") ]
do
  sleep 1
done
echo -e "...done\n"
exit 0