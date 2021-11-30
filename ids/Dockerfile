# This is the Dockerfile for the ids service which is needed to run icat.
# The Dockerfile can be run on its own or can be ran as part of a Docker 
# Compose suite of containers. The run.properties contains the name of the 
# icat service which is needed for it to connect to the icat service.

# Based on JDK8, also an option for JDK11
FROM payara/server-full:5.2021.7

# Define variables to use later on in this dockerfile. 
ARG IDS_VERSION=1.9.0
ARG IDS_STORAGE_PLUGIN_VERSION=1.4.1

# Download the contents of the ids plugin into the servers Home directory.
ADD https://repo.icatproject.org/repo/org/icatproject/ids.storage_file/$IDS_STORAGE_PLUGIN_VERSION/ids.storage_file-$IDS_STORAGE_PLUGIN_VERSION-distro.zip $HOME_DIR/

# Download the contents of the ids plugin into the servers deployment directory.
ADD https://repo.icatproject.org/repo/org/icatproject/ids.server/$IDS_VERSION/ids.server-$IDS_VERSION-distro.zip $DEPLOY_DIR/

# make the nessesary directories
RUN mkdir -p ~/data/main/link
RUN mkdir -p ~/data/main/prepared
RUN mkdir -p ~/data/archive
RUN mkdir -p ~/data/cache

ENV DEPLOY_PROPS=--libraries=ids.storage_file-$IDS_STORAGE_PLUGIN_VERSION.jar

# switch to root user and preform sudo actions for the IDS service
USER root

    # install dependancies and dev tools
    RUN apt-get update && apt-get install -y unzip zip nano net-tools curl

    # --- configure IDS plugin ---
    RUN unzip -j $HOME_DIR/ids.storage_file-$IDS_STORAGE_PLUGIN_VERSION-distro.zip ids.storage_file/ids.storage_file-$IDS_STORAGE_PLUGIN_VERSION.jar -d $HOME_DIR/appserver/glassfish/domains/domain1/lib/applibs \
    && rm $HOME_DIR/ids.storage_file-$IDS_STORAGE_PLUGIN_VERSION-distro.zip

    # --- configure IDS service ---
    # unzip the ids and remove zip
    RUN unzip $DEPLOY_DIR/ids.server-$IDS_VERSION-distro.zip -d $DEPLOY_DIR \
    && rm $DEPLOY_DIR/ids.server-$IDS_VERSION-distro.zip

    # Unpack the war file so we can copy in xml files
    RUN unzip $DEPLOY_DIR/ids.server/ids.server-$IDS_VERSION.war -d $DEPLOY_DIR/ids.server/unpacked
    RUN mv $DEPLOY_DIR/ids.server/* $DEPLOY_DIR/ \
    && rm -r $DEPLOY_DIR/ids.server/

    # put xml files into right place
    COPY config/run.properties $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY config/logback.xml $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY config/web.xml $DEPLOY_DIR/unpacked/WEB-INF/ 

    # remove old war file and repackage/rename new one
    RUN rm -r $DEPLOY_DIR/ids.server-$IDS_VERSION.war \
    && cd $DEPLOY_DIR/unpacked \
    && zip -r ids.server-$IDS_VERSION.zip ./WEB-INF ./META-INF \
    && mv $DEPLOY_DIR/unpacked/ids.server-$IDS_VERSION.zip $DEPLOY_DIR/ids.server-$IDS_VERSION.war \
    && rm -r $DEPLOY_DIR/unpacked

USER payara
RUN ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} start-domain ${DOMAIN_NAME} \
    # JVM
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} enable-secure-admin \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} create-jms-resource --restype javax.jms.Topic jms/IDS/log \
    && ${PAYARA_DIR}/bin/asadmin --user=${ADMIN_USER} --passwordfile=${PASSWORD_FILE} stop-domain ${DOMAIN_NAME} 
    
WORKDIR $HOME_DIR