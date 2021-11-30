# ICAT Cloud Native Migration  :whale:

[[_TOC_]]

This project stores the necessary configuration and code changes needed to migrate the ICAT application from a single VM installation to multiple, smaller micro-services.

The included Dockerfiles build on the official payara 5 docker image, installing the necessary system and application configuration, before deploying each component of ICAT in their own application server.

The diagram below shows the various components of ICAT and how they communicate inside the Docker network:

<img src="./documentation/images/icat cloud native architecture.png" width="920px" /> 



## Installation  

Docker is needed to run the ICAT suite of micro-services.

Google Chrome is needed to be able to log into Topcat.

Once the repository has been checked out, in a terminal, navigate to the folder holding the `docker-compose.yaml`. 

- run `docker-compose up --build`. To start the stack

- run `docker-compose down`. To destroy the stack

- :information_source: Note: run `docker system prune -a` to remove all images and containers

  

## List of Containers

### ICAT MariaDB container

Once running, the database can be logged into by either:

- using the adminer UI tool at http://localhost:8080/ using credentials:

  - Server = **icat_mariadb_container**
  - Username = **root**
  - password = **pw**
  - Database = **icatdb**

- logging into using mysql: `mysql -h 0.0.0.0 -P 3307 --protocol=TCP -u root -p`

  

### Topcat MariaDB container

Once running, the database can be logged into by either:

- using the adminer UI tool at http://localhost:8080/ using credentials:

  - Server = **topcat_mariadb_container**
  - Username = **root**
  - password = **pw**
  - Database = **topcat**

- logging into using mysql: `mysql -h 0.0.0.0 -P 2307 --protocol=TCP -u root -p`

  

### ICAT Server Payara container

Once running, the container can logged into by either:

- using the Payara UI tool at https://localhost:14848/ using **username/password: admin/admin**

- running `docker exec -it icat_payara_container bash` where `icat_payara_container` is the name of the running container,

- the version can be checked by going to https://localhost:18181/icat/version

  

### Authentication container

Once running, the container can logged into by either:

- using the Payara UI tool at https://localhost:24848/ using **username/password: admin/admin**

- running `docker exec -it auth_payara_container bash` where `auth_payara_container` is the name of the running container.

- the version can be checked by going to https://localhost:28181/authn.simple/version/

  

### IDS container

Once running, the container can logged into by either:

- using the Payara UI tool at https://localhost:34848/ using **username/password: admin/admin**

- running `docker exec -it ids_payara_container bash` where `ids_payara_container` is the name of the running container.

- the version can be checked by going to https://localhost:38181/ids/version/

  

### Lucene container

Once running, the container can logged into by either:

- using the Payara UI tool at https://localhost:44848/ using **username/password: admin/admin**

- Running `docker exec -it lucene_payara_container bash` where `lucene_payara_container` is the name of the running container.

- the version can be checked by going to https://localhost:48181/icat.lucene/version

  

### Topcat container

Once running, the container can logged into by either:

- using the Payara UI tool at https://localhost:54848/ using **username/password: admin/admin**

- Running `docker exec -it topcat_payara_container bash` where `topcat_payara_container` is the name of the running container.

- the version can be checked by going to https://localhost:58181/topcat/version/

- The Topcat web interface can be access by going to  https://localhost:58181/ 

  - Authentication type: **simple**
  - username: **root**
  - Password: **pw**

  

### Test data container

A separate container has been created to assist in adding some test data to be able to test the stack. Using the docker-compose `healthcheck` feature, it waits for the necessary tables to exist in the ICAT database before injecting some random test data. Once it has done this, it stops and the container is exited. This happens  automatically when starting the `docker-compose` stack. 

:information_source: Note that stopping and starting the suite of containers in `docker-compose` may cause certain errors to appear in the output, this is due to the applications trying to re-create tables where they already exist.



## Getting data out of the stack

As well as viewing the data through the Topcat web UI, curl can also be used to query ICAT directly from your local machine.

- `curl -k --data 'json={"plugin":"simple", "credentials": [{"username":"root"}, {"password": "pw"}]}' -w'\n' https://localhost:18181/icat/session` to get session id

- `curl -k --data "sessionId=[session id returned above]" --data-urlencode 'query=SELECT df.name, df.location, df.fileSize FROM Datafile df where df.fileSize < 10000000' --data "max=10" -w'\n' --get https://localhost:18181/icat/jpql`

  Should return something like:

  ```Count at least 5: [Datafile 39, /quite/minute/tough.gif, 6524978], [Datafile 48, /would/property/thousand.gif, 8998381], [Datafile 80, /poor/employee/dog.png, 5867347], [Datafile 82, /majority/win/interest.jpeg, 9014859], [Datafile 111, /remember/important/show.bmp, 9945264], [Datafile 114, /some/moment/population.bmp, 9172904], [Datafile 128, /skin/before/hundred.gif, 4223615], [Datafile 144, /campaign/from/me.tiff, 2387460], [Datafile 174, /structure/heart/particularly.tiff, 6980368], [Datafile 185, /fill/picture/yes.png, 246115]```

  

## List of Service URL's

The table below shows how the various components of icat can be accessed both internally to the docker network and externally from our host machines. Internal URLs can be used to ping one service from within another, external URLs can be used to ping services from our machine.

:information_source: **The internal URL's are mapped to container names and are set in the docker-compose file**. The database urls cannot be accessed directly over https in the browser.

| Service              | Internal URL                                | External URL             |
| -------------------- | ------------------------------------------- | ------------------------ |
| ICAT server          | http://icat_payara_container:8080           | https://localhost:14848/ |
| Auth Service         | http://auth_payara_container:8080           | https://localhost:24848/ |
| IDS Service          | http://ids_payara_container:8080            | https://localhost:34848/ |
| Lucene Service       | http://lucene_payara_container:8080         | https://localhost:44848/ |
| Topcat               | -                                           | https://localhost:54848/ |
| ICAT server database | http://icat_mariadb_container:3306/icatdb   | https://localhost:3306/  |
| Topcat database      | http://topcat_mariadb_container:3306/topcat | https://localhost:2306/  |



## The different configuration options

For now, there are two types of configuration to make:

- **Image configuration:** sets up the files and system properties the service needs to create the base image. This includes things like the web.xml and run.properties and any JVM settings to make.
- **Container configuration**: this is applied when the container is created and typically includes urls of other docker services, things that only exist once they have been started.

## Example start up

This is what starting up the cluster typically looks like. This is from scratch and includes the downloading and configuration of images, which would typically only be done once.

<img src="./documentation/images/2021-10-29 10.39.12.gif" width="920px" />



## Trouble shooting

### Ping one container from inside another 

This might be handy to debug any connection problems. For example; if we wanted to check that the ICAT container can see the IDS container, we could:

- Log into the ICAT container:

  `docker exec -it icat_payara_container bash`

- Get the version of the auth service:

  `curl -k https://auth_payara_container:8181/authn.simple/version/`

  or

  `curl http://auth_payara_container:8080/authn.simple/version/`

