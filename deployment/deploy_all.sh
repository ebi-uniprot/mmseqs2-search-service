#!/bin/bash
set -e

#=== Minikube initialization ===
minikube delete
minikube start --cpus=4 --memory=4g --disk-size=40g --driver=docker

#=== queue ===
helm install mmseqs2-queue oci://registry-1.docker.io/bitnamicharts/rabbitmq \
  --set auth.username=user \
  --set auth.password=mypassword123

cd ..

#=== meta-database ===
cd meta-database
docker build -t metadb:dev .
minikube image load metadb:dev
cd ../deployment
helm install mmseqs2-metadb ./db
cd ..

#=== worker ===
cd worker
docker build -t worker-consumer:dev .
minikube image load worker-consumer:dev 
cd ../deployment
helm install mmseqs2-worker ./worker
cd ..

#=== API ===
cd api
docker build -t api:dev .
minikube image load api:dev
cd ../deployment
helm install mmseqs2-api ./api
cd ..

sleep 10
minikube service mmseqs2-api --url