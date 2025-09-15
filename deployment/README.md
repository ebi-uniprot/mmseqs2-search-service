### start RabbitMQ using helm command

``` 
helm install my-release oci://registry-1.docker.io/bitnamicharts/rabbitmq 
```

### Before running helm deployment build the docker image locally

#### Build worker
```
cd worker
docker build -t worker-consumer:dev .
```
### build api docker image

```
cd api
docker build -t rest-api:dev .
```

#### build db docker image
``` 
cd db
docker build -t db:dev .
```