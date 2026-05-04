#!/usr/bin/env bash
LOG=.pihole_disable.log
PID_FILE=.pid

echo -e "\n======================" | tee -a $LOG
echo "=== PIHOLE_DISABLE ===" | tee -a $LOG
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