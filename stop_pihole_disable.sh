#!/usr/bin/env bash
LOGDIR=logs
LOGFILE=.pihole-disable.log
LOG=$LOGDIR/$LOGFILE
PID_FILE=.pid

if [ ! -d $LOGDIR ]
then
  mkdir $LOGDIR
fi

echo "======================" | tee -a $LOG
echo "=== PIHOLE-DISABLE ===" | tee -a $LOG
echo "======================" | tee -a $LOG

if [ -f $PID_FILE ]
then
  PID=$(<$PID_FILE)
else
  echo "No $PID_FILE file found!" | tee -a $LOG
  exit 1
fi

echo "Stopping Python script..." | tee -a $LOG
if [[ $(kill "$PID") -eq 0 ]]
then
  echo "...killed process $PID" | tee -a $LOG
  rm $PID_FILE
else
  echo "ERROR - process not stopped" | tee -a $LOG
  exit 1
fi

echo -e "Done\n" | tee -a $LOG
exit 0
