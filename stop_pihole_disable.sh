#!/usr/bin/env bash
APP=$PWD/pihole_disable.py

echo -e "\n======================"
echo "=== PIHOLE_DISABLE ==="
echo "======================"

echo "Creating STOP file..."
if [[ $(touch STOP) -eq 0 ]]
then
  echo "...done"
else
  echo "ERROR - STOP file not created"
  exit 1
fi

echo "Waiting for Python script to stop..."
while [ -z $(pgrep -f "$APP") ]
do
  sleep 1
done
echo -e "...done\n"
exit 0