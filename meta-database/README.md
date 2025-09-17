## Deploy MetaDatabase

#### Build metadb docker image

```
cd meta-database
docker build -t db:0.1.0 .
```

#### Load docker image in minikube

```
minikube profile list
minikube image load db:0.1.0 --profile=<PROFILE>
```

#### Delete metadb docker image from minikube if needed

```
helm uninstall mmseqs2-metadb
```

#### Deploy metadb in minikube

```
cd deployment
helm install mmseqs2-metadb db
```

Use http://mmseqs2-metadb:8080/ to connect to the metadb service
