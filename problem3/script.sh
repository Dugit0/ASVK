# Команды для сборки и запуска образов из исходников
docker build -t server:v01 server/
docker build -t client:v01 client/
docker network create -d bridge mynetwork
docker run --rm -d --name myserver --net mynetwork server:v01
docker run --rm -it --name myclient --net mynetwork client:v01 /bin/bash


# Команды для демонстрации решения на сайте https://labs.play-with-docker.com/
echo "FROM dugit0/server:v01" > dockerfile
docker build -t server_im .
echo "FROM dugit0/client:v01" > dockerfile
docker build -t client_im .
docker network create -d bridge mynetwork
docker run --rm -d --name myserver --net mynetwork server_im
docker run --rm -it --name myclient --net mynetwork client_im /bin/bash
python client.py

