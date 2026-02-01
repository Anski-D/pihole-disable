#!/usr/bin/env bash
APP=$PWD/pihole_disable.py
PORT=$1

echo -e "\n======================"
echo "=== PIHOLE_DISABLE ==="
echo "======================"

if [ -f STOP ]
then
  echo "Removing existing STOP file"
  rm STOP
fi

echo "Activating Python environment"
source .venv/bin/activate
echo "Starting script"
python "$APP" "$1" > .pihole_disable.log 2> .pihole_disable.err &
echo "Running $APP on port $1"
echo -e "Use $PWD/stop_pihole_disable.sh to terminate\n"
exit 0