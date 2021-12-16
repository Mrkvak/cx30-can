#!/bin/bash
# This script sends contents of file created by candump
if [ $# -ne 3 ]; then
	echo "Usage: $0 file delay caniface"
	exit 0
fi
FN=$1
DELAY=$2
IFACE=$3

sed 's/.*can[0-9]\s*\([0-9A-F]*\)\s*\[[0-9]*\]\s*\([0-9A-F]*\)/\1#\2/;s/ //g' "$FN" | while read l; do
	echo "Sending: $l to interface $IFACE"
	cansend $IFACE "$l"
	sleep $DELAY
done

