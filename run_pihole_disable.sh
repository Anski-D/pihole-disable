#!/usr/bin/env bash
LOGDIR=logs
LOGFILE=.pihole_disable.log
LOG=$LOGDIR/$LOGFILE
PORT=$1

if [ ! -d $LOGDIR ]
then
  mkdir $LOGDIR
fi

echo "======================" | tee -a $LOG
echo "=== PIHOLE_DISABLE ===" | tee -a $LOG
echo "======================" | tee -a $LOG

if [ -z "$PORT" ]
then
  echo -e "ERROR - port not provided\n" | tee -a $LOG
  exit 1
fi

echo "Activating Python environment" | tee -a $LOG
source .venv/bin/activate
echo "Starting script" | tee -a $LOG
hypercorn pihole_disable.main:app -b 127.0.0.1:"$PORT" -p .pid >> .pihole_disable.log 2>&1 &
echo "Running on port $PORT under process $!" | tee -a $LOG
echo -e "Use $PWD/stop_pihole_disable.sh to terminate\n" | tee -a $LOG

exit 0