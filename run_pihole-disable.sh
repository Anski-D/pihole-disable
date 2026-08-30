#!/usr/bin/env bash
# === USER INPUTS ===
LOG_DIR=logs
LOG_FILE=.pihole-disable.log
PORT=5000
WEB_SERVER_BIN=.venv/bin/hypercorn
# ===================

LOG=$LOG_DIR/$LOG_FILE
if [ -n "$1" ]
then
  PORT=$1
fi

if [ ! -d $LOG_DIR ]
then
  mkdir $LOG_DIR
fi

echo "======================" | tee -a $LOG
echo "=== PIHOLE-DISABLE ===" | tee -a $LOG
echo "======================" | tee -a $LOG

echo "Starting script" | tee -a $LOG
$WEB_SERVER_BIN pihole_disable.main:app -b 0.0.0.0:"$PORT" -p .pid >> $LOG 2>&1 &
echo "Running on port $PORT under process $!" | tee -a $LOG
echo -e "Use $PWD/stop_pihole_disable.sh to terminate\n" | tee -a $LOG

exit 0
