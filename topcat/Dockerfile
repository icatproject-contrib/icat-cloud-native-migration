# This is the Dockerfile for the topcat service

# Based on JDK8, also an option for JDK11
FROM payara/server-full:5.2021.7

# Define variables to use later on in this dockerfile. 
ARG TOPCAT_VERSION=2.4.8
ARG SQL_CONNECTOR_VERSION=mysql-connector-java-8.0.26.jar
ARG SQL_CONNECTOR_URL=https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.26/$SQL_CONNECTOR_VERSION
ARG DATASOURCE_CLASSNAME=com.mysql.cj.jdbc.MysqlDataSource

# Download the connector so topcat can access MariaDB
ADD $SQL_CONNECTOR_URL $PAYARA_DIR/glassfish/domains/domain1/lib/ext/

# Download the contents into the servers deployment directory.
ADD https://repo.icatproject.org/repo/org/icatproject/topcat/$TOPCAT_VERSION/topcat-$TOPCAT_VERSION-distro.zip $DEPLOY_DIR/

# create bin dir to hold the admin executables
RUN mkdir $HOME_DIR/bin

# switch to root user and preform sudo actions.
USER root

    #change permission so we can use later on
    RUN chmod 764 $PAYARA_DIR/glassfish/domains/domain1/lib/ext/$SQL_CONNECTOR_VERSION

    # install dependancies and dev tools
    RUN apt-get update && apt-get install -y unzip zip nano net-tools curl

    # unzip the ids and remove zip
    RUN unzip $DEPLOY_DIR/topcat-$TOPCAT_VERSION-distro.zip -d $DEPLOY_DIR \
    && rm $DEPLOY_DIR/topcat-$TOPCAT_VERSION-distro.zip

    # Unpack the war file so we can copy in xml files
    RUN unzip $DEPLOY_DIR/topcat/topcat-$TOPCAT_VERSION.war -d $DEPLOY_DIR/topcat/unpacked
    RUN mv $DEPLOY_DIR/topcat/* $DEPLOY_DIR/ \
    && rm -r $DEPLOY_DIR/topcat

    # put config files into right place
    COPY config/topcat.css $DEPLOY_DIR/
    COPY config/topcat.json $DEPLOY_DIR/unpacked/config/
    COPY config/lang.json $DEPLOY_DIR/unpacked/languages/
    COPY config/topcat.properties /opt/payara/
    COPY config/logback.xml $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY config/web.xml $DEPLOY_DIR/unpacked/WEB-INF/ 

    # move the pages dir and remove old directory
    RUN cp -r $DEPLOY_DIR/content.example/pages $DEPLOY_DIR/unpacked/pages
    # remove the migrations folder as there're not needed
    RUN rm -r $DEPLOY_DIR/migrations
    RUN rm -r $DEPLOY_DIR/content.example

    # move admin file
    RUN mv $DEPLOY_DIR/topcat_admin $HOME_DIR/bin 

    # remove old war file and repackage/rename new one
    RUN rm -r $DEPLOY_DIR/topcat-$TOPCAT_VERSION.war \
    && cd $DEPLOY_DIR/unpacked \
    && zip -r topcat-$TOPCAT_VERSION.zip .\
    && mv $DEPLOY_DIR/unpacked/topcat-$TOPCAT_VERSION.zip $DEPLOY_DIR/topcat-$TOPCAT_VERSION.war \
    && rm -r $DEPLOY_DIR/unpacked

USER payara
RUN ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} start-domain ${DOMAIN_NAME} \
    # JDBC
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} add-library $PAYARA_DIR/glassfish/domains/domain1/lib/ext/$SQL_CONNECTOR_VERSION \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jdbc-connection-pool --ping=true --steadyPoolSize=2 --datasourceClassname=$DATASOURCE_CLASSNAME --resType=javax.sql.DataSource --maxPoolSize=32 topcat \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jdbc-resource --connectionpoolid topcat jdbc/topcat \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} stop-domain ${DOMAIN_NAME} 
    
WORKDIR $HOME_DIR