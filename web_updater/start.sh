#!/bin/sh
# Use full paths ending with /. Make sure tables/ and templates/ folders exist in FULL_PATH_TO_OUTPUT
FULL_PATH_TO_DATA=~/Neurainodes/data/export/5241564e/
FULL_PATH_TO_OUTPUT=~/website/
./data_update.py $FULL_PATH_TO_DATA $FULL_PATH_TO_OUTPUT > logs/updater.log &
