#!/bin/bash
modprobe vcan
modprobe can-gw
ip link add dev vcan0 type vcan
ip link set up vcan0

ip link add dev vcan1 type vcan
ip link set up vcan1

cangw -F
cangw -A -s vcan0 -d vcan1 -e
cangw -A -s vcan1 -d vcan0 -e

