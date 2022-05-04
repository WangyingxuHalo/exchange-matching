#!/bin/bash
while [ "1"=="1" ]
do
    taskset -c 0 python3 /myroot/stockserver/server.py
    sleep 1
done