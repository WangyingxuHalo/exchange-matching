# Exchange Matching Engine
## Introduction
In this project, users can receive xml data to sell or buy stock. Each buy order can be matched to a proper sell order. Each sell order can be matched to a proper buy order.

## Member:
Congjia Yu | cy146<br>
Yingxu Wang | yw473

## Steps to run server.py:
1. Go to directory: docker-deploy/erss-hwk4-cy146-yw473
2. Run command: sudo docker-compose up

## Steps to run client.py: (Our testing)
1. Go to directory: docker-deploy/erss-hwk4-cy146-yw473/src/testing
2. Run python3 client.py

## Methods to change the core number for server: (You may change the path to the directory in your computer)
### 1 core:
taskset -c 0 python3 ~/ece568/erss-hwk4-cy146-yw473/docker-deploy/erss-hwk4-cy146-yw473/src/stockserver/server.py
### 2 cores:
taskset -c 0-1 python3 ~/ece568/erss-hwk4-cy146-yw473/docker-deploy/erss-hwk4-cy146-yw473/src/stockserver/server.py
### 3 cores:
taskset -c 0-3 python3 ~/ece568/erss-hwk4-cy146-yw473/docker-deploy/erss-hwk4-cy146-yw473/src/stockserver/server.py
