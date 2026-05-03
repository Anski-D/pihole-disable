#!/usr/bin/env bash
APP=$PWD/app.py
PORT=$1
FLASK_DEBUG=1
export FLASK_DEBUG

echo -e "\n======================"
echo "=== PIHOLE_DISABLE ==="
echo "======================"

if [ -z "$PORT" ]
then
  echo -e "ERROR - port not provided\n"
  exit 1
fi

if [ -f STOP ]
then
  echo "Removing existing STOP file"
  rm STOP
fi

echo "Activating Python environment"
source .venv/bin/activate
echo "Starting script"
gunicorn app:app --bind 127.0.0.1:"$PORT" > .pihole_disable.log 2> .pihole_disable.err &
PID=$!
echo "Running $APP on port $PORT under process $PID"
echo -e "Use $PWD/stop_pihole_disable.sh to terminate\n"

while [ ! -f STOP ]
do
  sleep 1
done
kill $PID

exit 0