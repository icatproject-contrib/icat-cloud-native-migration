# This is the Dockerfile for the icat.server service which is needed to run icat.
# The Dockerfile can be run on its own but won't deploy correctly as it needs the 
# auth service running. It can also be ran as part of a Docker Compose suite of
# containers. The run.properties contains the name of the auth container which 
# is needed for icat to connect to the auth service.

# Based on JDK8, also an option for JDK11
FROM payara/server-full:5.2021.7

# Define variables to use later on in this dockerfile. 
ARG ICAT_VERSION=5.0.0
ARG SQL_CONNECTOR_VERSION=mysql-connector-java-8.0.26.jar
ARG SQL_CONNECTOR_URL=https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.26/$SQL_CONNECTOR_VERSION
ARG DATASOURCE_CLASSNAME=com.mysql.cj.jdbc.MysqlDataSource

# Download the connector so ICAT can access MariaDB
ADD $SQL_CONNECTOR_URL $PAYARA_DIR/glassfish/domains/domain1/lib/ext/

# Download the contents of the ICAT Version into the servers deployment directory.
ADD https://repo.icatproject.org/repo/org/icatproject/icat.server/$ICAT_VERSION/icat.server-$ICAT_VERSION-distro.zip $DEPLOY_DIR/

# create bin dir to hold the testicat and icatadmin executables
RUN mkdir $HOME_DIR/bin

# switch to root user and preform sudo actions
USER root

    #change permission so we can use later on
    RUN chmod 764 $PAYARA_DIR/glassfish/domains/domain1/lib/ext/$SQL_CONNECTOR_VERSION

    # install dependancies and dev tools
    RUN apt-get update && apt-get install -y unzip zip nano net-tools curl

    # unzip the icat server and remove zip
    RUN unzip $DEPLOY_DIR/icat.server-$ICAT_VERSION-distro.zip -d $DEPLOY_DIR \
    && rm $DEPLOY_DIR/icat.server-$ICAT_VERSION-distro.zip

    # Unpack the war file so we can copy in xml files
    RUN unzip $DEPLOY_DIR/icat.server/icat.server-$ICAT_VERSION.war -d $DEPLOY_DIR/icat.server/unpacked
    RUN mv $DEPLOY_DIR/icat.server/* $DEPLOY_DIR/ \
    && rm -r $DEPLOY_DIR/icat.server/

    # move xml files over
    COPY config/web.xml $DEPLOY_DIR/unpacked/WEB-INF/ 
    COPY config/persistence.xml $DEPLOY_DIR/unpacked/WEB-INF/classes/META-INF/ 
    COPY config/run.properties $DEPLOY_DIR/unpacked/WEB-INF/classes/ 
    COPY config/logback.xml $DEPLOY_DIR/unpacked/WEB-INF/classes/

    # icat needs this file on deployment, this is needed as the default start up directory is different. It does nothing
    RUN touch /opt/payara/glassfish-acc.xml

    # remove old war file and repackage/rename new one
    RUN rm -r $DEPLOY_DIR/icat.server-$ICAT_VERSION.war \
    && cd $DEPLOY_DIR/unpacked \
    && zip -r icat.server-$ICAT_VERSION.zip ./WEB-INF ./META-INF \
    && mv $DEPLOY_DIR/unpacked/icat.server-$ICAT_VERSION.zip $DEPLOY_DIR/icat.server-$ICAT_VERSION.war \
    && rm -r $DEPLOY_DIR/unpacked
    
    # move admin and test files
    RUN mv $DEPLOY_DIR/icatadmin $HOME_DIR/bin \
    && mv $DEPLOY_DIR/testicat $HOME_DIR/bin 

# - Run asadmin commands that setup script does. The rest is done on container start
USER payara
RUN ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} start-domain ${DOMAIN_NAME} \
    # JDBC connector
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} add-library $PAYARA_DIR/glassfish/domains/domain1/lib/ext/$SQL_CONNECTOR_VERSION \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jdbc-connection-pool --ping=true --steadyPoolSize=2 --datasourceClassname=$DATASOURCE_CLASSNAME --resType=javax.sql.DataSource --maxPoolSize=32 icat \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jdbc-resource --connectionpoolid icat jdbc/icat \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jms-resource --restype javax.jms.Topic jms/ICAT/Topic \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jms-resource --restype javax.jms.Topic jms/ICAT/log \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} stop-domain ${DOMAIN_NAME} 
    
WORKDIR $HOME_DIR

