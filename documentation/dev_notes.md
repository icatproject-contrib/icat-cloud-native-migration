# ICAT cloud native migration notes:

[TOC]

This document will hold my development notes whilst working on migration of the ICAT application from one big centos7 image, to multiple smaller micro-services. 

It is a work in progress and will evolve over time.

## :arrow_right: Introduction to Docker

- Docker is pretty much like Vagrant. It allows the creation of vm's.
- The vm's, or images are smaller as they are mostly dedicated to one thing.
- This fosters a modular approach to design but increases network overhead
- Images are referenced by creating what's called a `Dockerfile`
- This pulls down any base image needed and applies some basic configuration.
- Running the Dockerfile creates a Container which is based from a base image.
- More advanced configurations can be copied into the container, through the docker file, and ran on startup.
- Here's a quick [guide to docker](https://medium.com/@moonraker/an-introduction-to-docker-a0d9620e58c6) I created a while ago which may help explain some fundamentals if needed.
- Docker has its own "docker setup" scripting tool : `docker-compose` to manage simultaneous start/stop and some configuration of these Dockerfiles. It also allows custom initialisation and network settings configuration.
- Here's an example docker-compose file from the NID in DAFNI, that sets up Postgres database to work with, accessible on localhost on port 5003

```yaml
version: '3.5'

services:
  nidpostgres:
    restart: always
    image: postgres:11
    container_name: nidpostgres
    ports: 
      - "5003:5432"
    environment:
        POSTGRES_PASSWORD: password
        POSTGRES_USER: nidpostgres
        POSTGRES_DB: nid
```

- It also allows you to run a docker file for code that **you're developing locally** in the same list.

- For example, this is how the nid's server application is deployed to a docker image and the various dependency addresses fed in to the application.

- NOTE: the `build: .` refers to a `Dockerfile` which is based on a python3 image.

```yaml
  nid:
     restart: always
     build: .
     image: nid
     depends_on:
       - nidpostgres
     container_name: nid
     ports:
       - "5000:5000"
     environment:
       DATABASE_HOST: 'nidpostgres'
       DEBUG: "True"
```



### Images VS Containers

Images are non-changeable templates. Generally images are bigger, take longer to build and is where most of the configuration should take place. Images are the thing docker builds once and containers are instances of containers. Images can sometime take 5-10 minutes to build where containers should be spun up in seconds. Building an image say, pulls down an OS, python and any frameworks needed and packages it all up, Containers are just a running instance of that image and there can be many instances of that image, or many containers based on that image. Containers are the thing K8s would spin up dependant on load and would be constantly creating destroying containers based on availability.

The line between image configuration and container config is blurred, mainly down to the fact that you can specify bash scripts to run on container startup. For example:

` docker run -p 8080:8080 -v pathtoICATServer -e POSTBOOT_COMMANDS=/config/post-boot-commands.asadmin payara/server-full`

- Creates a container based on `payara/server-full`
- Copies in either a local or online version of icat
- Runs a post boot script

## :arrow_right: What this means for ICAT

- For icat, this would mean that code development could be done locally instead of within one big vm. It can then be deployed to a container for testing. This is good because it would mimic production.
- Ideas: we could:
  - manage our own custom docker repo to store any custom base images to pull / push images from. We could probably make do with the publicly available one for the time being , if there are no safety concerns.
  - These images could be pulled to create containers which would be used with the Jenkins Continuous Integration Environments, like staging (pre-prod) and prod etc
  - In the long run, Kubernetes would be needed to manage the containers in these environments.
- Whist following the tutorial, it looks like each image may have a fair bit of configuration applied to it. 
- Need to figure out the grand plan of how these containers fit into the CI environment, here is Stuarts doc that explains most of that: 
  - https://hackmd.io/iWsy-NYCToOYP-J7wdtdrQ?view

## :arrow_right: Architectural Overview

<img src="./images/icat cloud native architecture.png" width="920px" />


## :arrow_right: Work plan

- [x] Seems like a good idea to get a known working tool up and running in a container first; MariaDB
- [x] Look into containerising Payara and map config across
  - [x] Deploy icat server inside it as an asadmin application
- [x] Look into containerising auth plugin
- [x] Look into containerising the IDS?
- [ ] Look into containerising the Lucene component
- [x] Look at docker-composing the lot together 
- [ ] Topcat
- [ ] Get ICAT code, build and run locally against containers



## :arrow_right: Docker files vs docker-compose

- Going to get containers working out of Dockerfiles. This makes more sense as any deployment will need docker files rather than a docker-compose file. docker-compose is mainly used to get systems up and running locally.
- Plus, some operations like copying content into the container can only be done in dockerfiles: 
  `COPY x Y`
- Environment variables can be passed in, in docker files, by using `ENV` keyword; for example:
   `ENV MARIADB_DATABASE icatdb`



## :arrow_right: MariaDB

- ICAT running version `5.5.68-MariaDB MariaDB Server`
- [Official docker images](https://hub.docker.com/_/mariadb/) only supports `v10.xx`
- Going to try and use latest version otherwise will look at creating my own Dockerfile
- `default_storage_engine` set to InnoDB by default
- No option for `secure_installation`
- `mysql_secure_installation` will need to be automated if really needed, for now I think its fine as I'm working on local deployment. Plus prod is a managed database? Use `expect` if needed.
- New users created in docker file are given domain `@localhost` by default
- Connecting to mariadb in container using: `mysql -h 0.0.0.0 -P 3307 --protocol=TCP -u root -p` from docker host machine (my Mac).



## :arrow_right: Payara

### Configuring the Container

- ICAT running Payara version 4.1.2.181
  - There are several versions to [choose from now](https://hub.docker.com/u/payara/?hsCtaTracking=916ae074-a75f-4aec-87d6-25cf09005c9a%7C92cc9f55-20a7-48c8-9d83-d36ddb23980b); micro, server-web, server-node and server-full
- Using `payara/server-full:5.2021.5`, which uses JDK8
  - option to use JDK11 is available
- Web UI at https://localhost:4848 username/pasword = admin
- `docker exec -it docker_payara_1 bash` to have a look around inside the container
- Going through the list of setup activities in the icat tutorial [here](https://github.com/icatproject/icat.manual/blob/master/tutorials/03InstallingGlassFish.md)
- Trying to map the paths used in the tutorial to the new paths created in the container
- List of asadmin tasks to run from [setup-glassfish.py](https://github.com/icatproject/icat.utils/blob/master/src/main/scripts/setup-glassfish.py). These are in a python file which can't run on the payara docker image, so will need to be translated into `.asadmin` file which can be ran on start up.
- The original script was run by: `python scripts/setup-glassfish.py domain1 75% pw`
  - `domain1` set by default
  - 75% used in `-Xmx` option
  - pw used so the mariadb and payara passwords are the same.
- The .asadmin file can be loaded into docker as a **pre-boot** configuration file. Setting it as a **post-boot** config means the server needs restarting which we can't do.
- List of `list-vm-options` discrepancies (excel spreadsheet [here](./list-jvm-options.xlsx)), But basically:
  - **In Local Vagrant but NOT in container**, i.e: potential to add to container:
    - `-XX:MaxPermSize192m` 
    - `-client`
    - `-Djdbc.driversorg.apache.derby.jdbc.ClientDriver`
    - `-Xmx365m`
    - `-XX:OnOutOfMemoryError"kill -9 %p"`
  - **In container but NOT in local Vagrant set up** (of significance),  i.e: potential to remove:
    - `-Dorg.glassfish.grizzly.nio.DefaultSelectorHandler.force-selector-spin-detection=TRUE`
    - `-Xbootclasspath/a:${com.sun.aas.installRoot}/lib/grizzly-npn-api.jar   --> JDK versions: min(1.8.0.251)`
    - `-XX:MaxRAMPercentage=${ENV=MEM_MAX_RAM_PERCENTAGE}`
    - `-Xss${ENV=MEM_XSS}`
    - `-Djdbc.drivers=org.h2.Driver`
    - `-server`
- replacing `-XX:OnOutOfMemoryError="kill -9 %p"` with `-XX:+ExitOnOutOfMemoryError` 
  - The app won't need restarting, just exit and let docker restart on failure `--restart unless-stopped`
  - Needs testing
- I think the `-Djdbc.driversorg.apache.derby.jdbc.ClientDriver` option along with the connection pool to mariadb get set up in the icat application installation 
- `MaxPermSize` is ignored in JDK8; [here](https://stackoverflow.com/questions/33915849/java-8-outofmemory-error-change-maxpermsize)
- `XMX` option: `+UseContainerSupport` (enabled by default) allows The JVM to calculate its memory based on The memory allocated to The container so nothing to do there.



## :arrow_right: Running ICAT inside Payara

- Looking into pull the ICAT zip down from gitlab then unpacking it inside the payara container, meaning I don't have to have a local copy to `COPY` into the container.
- Logs are stored at `~/appserver/glassfish/domains/domain1/logs/`
- Need to unzip as distros are zips not tar.gz
- Using `jar -xvf ....` instead of installing `unzip` which saves loading time
- Only root can do this however so having to switch user in docker file
- Going to copy in icat config files locally (meeting with Stuart), the rest will be pulled from online repo
- Log path needs to be changed as presumably paths changed changed in payara 5 
- The divide of **what to put in image** config and **what to put in container start up**:
  - Putting as much config in the image is best as this will allow containers to boot quicker
  - Putting config into the container should only be done where the containers need to be different but based on the same image.
  - For example; we want to put jvm and basic payara set up in the image so we can base all icat containers using the same image.

### Image VS Container Configuration split for ICAT (where to run the setup script from)

Ideally we'd set up the payara image with everything it needs to run and build it, and when starting a container, pass it the setup config files and run the setup script. This would allow the user to create multiple instances of the same version of ICAT but with differently configured settings. Ideas:

#### Using volume mounts

- Mounting a volume at container start
- Creating a custom entry point script defined in the image file
- Entry point script would call python set up and use config shared in volume mount

**However**, the issue with this is that the payara and docker have a specific start up sequence. Payara defines an ENTRYPOINT for containers to start so we'd need to define our own, which would run a setup script before calling the normal entry point. This isn't working with some kind of threading errors probably because payaras' entry point is called with a framework called [tini](https://docs.payara.fish/community/docs/documentation/ecosystem/docker-images/server-image-overview.html#default-entrypoint). 

#### Using the INIT_ method

Payara allows for customs bash scripts to be ran on start up. 

- Write a bash script that called the python script
- Std output is disabled for this so would need to log to log file

**However**,  all output is hidden and not sent to stdout so it makes dev hard.

For this reason we'll copy the all the configuration over and run the setup scripts on image build.

### ICAT Set Up Script (how to apply the setup)

- The issue with the setup script is that someone has put a lot of work into setting up icat, trying to account for multiple system configurations, Operating system, weather directories exist, weather certain db connections exist, all of which go away in the docker world as we always start from a defined starting point. Specifically it:
  - It checks that the properties files against the properties.example file and notifies the user if they don’t match. This seems a bit unnecessary given that we’ll need to pass the config files in at image build time.
  - Check the OS is windows or otherwise and sets some paths up.
  - Wildfly, its all glassfish
  - It checks things like paths. for example: setup.properties has: home = /opt/payara/appserver, which is fixed in the payara container and unnecessary to define.
  - Checks versions of glassfish and asadmin
  - Check passwords are set up
  - The rest of the setup and run properties variables could be passed in as environment variables, removing the need to copy in config files altogether.
  - It does a lot of uninstalling stuff which is unnecessary in the docker setup

#### How to run, or provide the same setup that the python script provides?

1. Run the python set up script

   - Run at image build time:

     - :skull_and_crossbones: Failing due to `asadmin` permissions in the script. It seems that all `asadmin` commands in user space need credentials which the script doesn't give. The script can't run: `/opt/payara/appserver/bin/asadmin --port 4848 get property.administrative.domain.name`

       This is because the [setup glass fish script](https://github.com/icatproject/icat.utils/blob/4f4d907e431202aa73d5dc796c19918b73bba8f7/src/main/scripts/setup-glassfish.py#L104) uses `--savelogin` so we don't need it later on. It does this when it creates the domain, something that we don't do in the docker image. The payara docker container comes with domain1 pre-created

     - Run as a $POSTBOOT step:

       - :skull_and_crossbones: Can't do this because all pre and post boot commands are means for asadmin commands, not running python scripts

     - Run as a init_.sh file

       - :skull_and_crossbones: There doesn't seem to be any std output for commands ran this way
       
         

2. Re-write the python script in bash so it can be applied on startup.

3. Edit & Run the setup script manually once the container has started, save the image on docker hub, allowing people to pull it down:

   - Still have same permission issues as above
   - Besides, this has the following drawbacks:
     - Raulfs docker images are completely custom where he installs opensuse and goes from there
       - This means that the images are bigger
       - Versioning becomes difficult as everything is installed separately e.g java, glass fish etc
       - Abstraction due to layers of custom dockerfiles
     - Creating our own image means that configuration wouldn't be possible as the run and setup properties are needed to set the image up, not the container.
     - If payara needed updating we would have to create the image all over again

So Based on this we have options:

1) Doctor the set up script so that it works on startup
   - **Pros**: Least architectural change.
   - **Cons**: This will mean that that the updated python script will need to cater for the docker setup (probably by passing it a flag or something) and the normal installation process. This will probably involve a fair bit of testing as all the existing installation process may need to be tested again.
2) Create a new setup script dedicated to docker 
   - **Pros**: easy to do
   - **Cons**: code bloat, still need to install python to do file manipulation.
3) Rewrite the setup in bash: :thumbsup: :thumbsup: :thumbsup: :thumbsup:
   - **Pros**: lean and dedicated setup script without all the unnecessary error checking with doesn't apply to the docker container 
   - **Cons**: The script contains a load of file changing which would be difficult in bash so for now we'll hold a local copy of the files pre-changed and copy them over, into the image.

### What the set-up script does

#### Setup Database

- `asadmin create-jdbc-connection-pool --datasourceclassname com.mysql.jdbc.jdbc2.optional.MysqlDataSource --property url=jdbc:mysql://localhost:3306/icatdb:user=icatdbuser:password=icatdbuserpw --restype javax.sql.DataSource --failconnection=true --steadypoolsize 2 --maxpoolsize 32 --ping icat`

- `asadmin create-jdbc-resource --connectionpoolid icat jdbc/icat`
- `asadmin create-jms-resource --restype javax.jms.Topic jms/ICAT/Topic`
- `asadmin create-jms-resource --restype javax.jms.Topic jms/ICAT/log`

#### Setup Deploy

- UnZipps war file and copies it into an unzipped folder
- In **unzipped/WEB-INF/web.xml** changes
  - transport-guarantee from CONFIDENTIAL to NONE
  - Replaces text in web-app/servlet/servlet-class to "org.glassfish.jersey.servlet.ServletContainer"
  - Removes all children of context-param
- In **unzipped/WEB-INF/glassfish-ejb-jar.xml** changes
  - transport-guarantee from CONFIDENTIAL to NONE
  - Replaces text in mdb-connection-factory/jndi-name with "icatProperties.get("jms.topicConnectionFactory"
- In **unzipped/WEB-INF/classes/META-INF/persistence.xml** changes
  - Value of property/eclipselink.target-server = Glassfish
  - Value of property/eclipselink.logging.level = OFF
  - Value of property/eclipselink.logging.level.sql = OFF
  - Value of property/eclipselink.logging.parameters = false
- Zips it all back up
- `asadmin deploy --deploymentorder 100` + some crazy for loop
- Moves "testicat", "icatadmin" to binDir

### Connection to mariaDB from Payara

- Had to change data source class name from

  -  `com.mysql.jdbc.jdbc2.optional.MysqlDataSource` 

    to 

  - `com.mysql.cj.jdbc.MysqlDataSource `
  
- Upgraded sql connector from 5 to 8

### Deployment of icat-server

- Deployment of icat application failing due to `class org.icatproject.core.IcatException No authenticator of type simple is working`
  - This had to be done manually inside the admin UI because of below issue. 
  - Remove the security layer of the web.xml so we can talk over http
- Deployment failing on container start due to bug in Payara. Question ask and answered [here](https://stackoverflow.com/questions/69117678/deploy-war-file-in-payara-5-docker-container)
- Deployment now failing due the fact that icat can't find `glassfish-acc.xml` . It does exist in the container but the starting payara directory is different.
  - To solve this, I'm just creating the file in `/opt/payara/glassfish-acc.xm`. Should probably fix the code in icat https://github.com/icatproject/icat.utils/blob/master/src/main/java/org/icatproject/utils/ContainerGetter.java

### Ping auth container from icat container

- `curl -k https://auth_payara_container:8181/authn.simple/version/`
- `nmap -p 8181 auth_payara_container`

## :arrow_right: Authentication

Setting up the Auth image, which should address one of the icat issues above

- Its needs the same connection to Mariadb
- Deploys successfully manually after start
- Errors with ejb missing when using papayas auto deploy version` 5.2021.7`, stack [here](https://stackoverflow.com/questions/69222666/payara-automactic-deployment-ejb-error-but-not-manually)
- When doing it manually its running:
- `deploy --keepState=false --virtualservers=server --precompilejsp=false --availabilityEnabled=false --name=authn.simple-2.0.0 --verify=false --force=false --enabled=true --properties=implicitCdiEnabled=true:preserveAppScopedResources=false:cdiDevModeEnabled=false --target=server /opt/payara/deployments/authn.simple/authn.simple-2.0.0.war`
- Issue was with the intermediate folder in the deployment dir, removing that and having the war directly in $DEPLOY_DIR makes it deploy.
- Issue with icat service not being able to connect to Auth service
  - This was due to the fact that I didn't have a web.xml for the auth service and had the security layer enabled in icat's web.xml
  - Removing this means I can now communicate, both internally and externally of http not https and so no certification is needed
  - `curl http://auth_payara_container:8080/authn.simple/version/` from with icat.server container
- Bash into container using `docker exec -it auth_payara_container bash`
- Ping icat from with container `curl http://icat_payara_container:8080/icat/version/`

## :arrow_right: IDS

- Getting error: class java.lang.ClassNotFoundException org.icatproject.ids.storage.ZipMapper
- Need to put jar lib file in the right place.
  - Vagrant: /home/glassfish/payara41/glassfish/domains/domain1/lib/applibs
- Ping ids from icat `curl http://ids_payara_container:8080/ids/version/`

## :arrow_right: Lucene

- Make sure to update allowed Ip address: we don't have access to individual IP address as docker/docker-compose assigns these when creating the container, so changed to `0.0.0.0/0` to allow everything.

- Ping lucene from my machine:
  - curl -k https://localhost:48181/icat.lucene/version
- Ping lucene from another container:
  - `curl http://lucene_payara_container:8080/icat.lucene/version`
- Ping lucene from with lucene:
  - `curl http://127.0.0.1:8080/icat.lucene/version`

## :arrow_right: Adding Test Data:

- Using script [here](https://github.com/ral-facilities/datagateway-api/blob/master/util/icat_db_generator.py)

- Cd to data gateway-api folder

- Run `python3.6 -m util.icat_db_generator -s 4 -y 1` with the icat docker suite up and running, should take around 5-10 mins

  - With config ( `0.0.0.0:3306` is our `icat_mariadb_container`):

    ```
    {
      "backend": "db",
      "db_url": "mysql+pymysql://icatdbuser:icatdbuserpw@0.0.0.0:3306/icatdb",
      "log_level": "WARN",
      "log_location": "/logs.log",
      "generate_swagger": false
    }
    ```

  - Testing icat returns data from within ids container:

    ```
    curl -k --data 'json={"plugin":"simple", "credentials": [{"username":"root"}, {"password": "pw"}]}' -w'\n' http://icat_payara_container:8080/icat/session
    ```

  - Testing icat returns data from my mac:

    ```
    curl -k --data 'json={"plugin":"simple", "credentials": [{"username":"root"}, {"password": "pw"}]}' -w'\n' https://localhost:18181/icat/session
    ```


## :arrow_right: Topcat

- Had to refactor db setup as had to create a new data base for tomcat, couldn't use the existing icat

  <img src="./images/mariadb_setup.png" width="520px" />

  - All database comms inside docker is done on port 3306
  
  - This is because the address is resolved by host name in the Docker file:
    - `ARG DATABASE_URL=jdbc:mysql://topcat_mariadb_container:3306/topcat`
    
  - `topcat.properties`is store in
  
    - Old world: `home/glassfish/payara41/glassfish/domain1/config`
    - New world: `payara/appserver/glassfish/domains/domain1/config`
  
  - The `contents/pages` directory is copied into the root level of the war file before it is re-packed
  
  - Getting `Archive type of /opt/payara/deployments/migrations was not recognized` error
  
    - I think its because its trying to deploy the folder because its in the deploy dir
  
  - `facility.LILS.downloadType.http` should be ids url so:
  
    - `facility.LILS.downloadType.http` = http://ids_payara_container:8080
  
  - Needed to setup the mail javamail-resource
  
  - Needed to copy all of the contents of the distro into the war file, not just the META and WEB inf
  
  - Can only log in using CHROME, Firefox says no!
  
    

## :arrow_right: Adding Test Data Automatically on start:

- Instead of having to run the script to add test data every time the docker stack is brought down and up, it would be better to automate it so that test data is automatically injected when the containers are started.

- Using the data gateway-api utils script, copying it into a container running the script after the db and icat have successfully started

- Data can bee seen using admirer at http://localhost:8080:

  - Server = icat_mariadb_container
  - Username = root
  - password = pw
  - Database = icatdb

- To get test data from my Mac run:

  - `curl -k --data 'json={"plugin":"simple", "credentials": [{"username":"root"}, {"password": "pw"}]}' -w'\n' https://localhost:18181/icat/session` to get session id.

  - `curl -k --data "sessionId=aa923fd0-056b-4dca-bf31-9d6659b69bdf" --data-urlencode 'query=SELECT df.name, df.location, df.fileSize FROM Datafile df where df.fileSize < 10000000' --data "max=10" -w'\n' --get https://localhost:18181/icat/jpql`

    Should return something like:

  ```bash
  Count at least 5: [Datafile 39, /quite/minute/tough.gif, 6524978], [Datafile 48, /would/property/thousand.gif, 8998381], [Datafile 80, /poor/employee/dog.png, 5867347], [Datafile 82, /majority/win/interest.jpeg, 9014859], [Datafile 111, /remember/important/show.bmp, 9945264], [Datafile 114, /some/moment/population.bmp, 9172904], [Datafile 128, /skin/before/hundred.gif, 4223615], [Datafile 144, /campaign/from/me.tiff, 2387460], [Datafile 174, /structure/heart/particularly.tiff, 6980368], [Datafile 185, /fill/picture/yes.png, 246115]
  ```

  - The testdata container needs the mariadb and the icat payara app to be up and running. This is because the icat payara app creates the tables.
    - Mariadb starts and creates the icat database
    
    - Icat-server starts and add the tables, runs the migrations
    
    - Only then can the testdata container run and put data into the tables
    
      

## :arrow_right: DataGateWay

- The replacement for topcat
- Consists of the following API's;
  - https://github.com/ral-facilities/datagateway
  - https://github.com/ral-facilities/scigateway
  - https://github.com/ral-facilities/datagateway-api
  - https://github.com/ral-facilities/scigateway-auth/
- Docs https://github.com/ral-facilities/scigateway/wiki
- Example UI [scigateway-preprod.esc.rl.ac.uk/](http://scigateway-preprod.esc.rl.ac.uk/) 
- Starting with auth

### Scigateway-auth

- No distros yet so need to pull down raw git repo
- The poetry framework make installing the dependancies easy
- Generatering keys inside container

---------------------------------------------------

## :arrow_right: Todo, Technical Dept and Improvement ideas :bulb:

- [x] Get topcat deployed

- [x] Add test data automatically, create a container with the data gateway api in it so I can use the script to auto generate test data on startup
  - [x] Optimise icat health check 
  - [x] Sort mariadb warning 
  - [x] Refactor lay out 
  - [x] Remove miriadb docker file as do everything through docker-compose 
  - [x] Get rid of config and use env files for testdata container
  - [x] sort commands/config name convention out 
  - [x] Document compose health check setup 
  
- [x] Document config setup in readme

- [ ] Get datagatway deployed

- [ ] Get icat working with Lucene

- [x] Look into splitting config out for icat to pass in at container run

- [ ] Prep for presentations, why use docker, how does it help deployments, what are the step to get to fully auto deployments

- [ ] Look into update to JDK from 8 to 11

- [ ] Look into deploying an oracle DB in docker

- [ ] Change master password from `admin` to `pw`, example of this [here](https://stackoverflow.com/questions/47411022/change-master-password-on-payara-glassfish-server#47453368), use password files, or use vault and change ui admin/admin

- [ ] Fix allowed ip addresses in lucene

- [ ] Change ICAT to use environment variables instead of config files

- [ ] Need to generally do some load testing of icat to test jvm memory options which are set by default by the container
  - [ ] Good application of this from divileroo [here](https://deliveroo.engineering/2019/01/08/how-to-debug-memory-usage-of-a-jvm-based-application.html)
  - [ ] Test `ExitOnOutOfMemoryError` vs `OnOutOfMemoryError` and other jvm options
  
- [ ] Automate the `mysql_secure_installation` for the database, [resource here](https://stackoverflow.com/questions/24270733/automate-mysql-secure-installation-with-echo-command-via-a-shell-script#27759061), if needed

- [ ] Put all the docker images in their respective repos instead of one big repo

- [ ] Persistent files/volumes for ids and lucene

  

  Datagateway Auth:

- [ ] Sort out creating keys outside of image.

- [ ] App to check config on app start

  

  

