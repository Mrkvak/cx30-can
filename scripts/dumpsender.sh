#!/bin/bash
# This script sends contents of file created by candump
if [ $# -ne 2 ]; then
	echo "Usage: $0 file caniface"
	exit 0
fi
FN=$1
IFACE=$3

sed 's/.*\([0-9\.]*\)\s*can[0-9]\s*\([0-9A-F]*\)\s*\[[0-9]*\]\s*\([0-9A-F]*\)/\1 \2#\3/;s/ //g' "$FN" | while read l; do
	DELAY=$(echo $l | cut -d " " -f 1)
	CMD=$(echo $l | cut -d " " -f 2)
	sleep $((DELAY-0.01))
	echo "Sending: $CMD to interface $IFACE"
	cansend $IFACE "$CMD"
done

