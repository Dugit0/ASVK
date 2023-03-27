#!/bin/bash

docker build -t server:v01 server/
docker build -t client:v01 client/
docker network create -d bridge mynetwork

docker run --rm -d --name myserver --net mynetwork server:v01
# docker run --rm -d --name myclient --net mynetwork client:v01
docker run --rm -it --name myclient --net mynetwork client:v01 /bin/bash

