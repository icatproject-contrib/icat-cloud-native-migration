# This is the Dockerfile for the auth service which is needed to run icat.
# The Dockerfile can be run on its own or as part of a docker Compose suite 
# of containers.

# Based on JDK8, also an option for JDK11
FROM payara/server-full:5.2022.5

# Define variables to use later on in this dockerfile. 
ARG AUTH_VERSION=2.0.1

# Download the contents of the auth plugin into the servers deployment directory.
ADD https://repo.icatproject.org/repo/org/icatproject/authn.simple/$AUTH_VERSION/authn.simple-$AUTH_VERSION-distro.zip $DEPLOY_DIR/
ADD https://repo.icatproject.org/repo/org/icatproject/authn.anon/$AUTH_VERSION/authn.anon-$AUTH_VERSION-distro.zip $DEPLOY_DIR/

# switch to root user and preform sudo actions
USER root

    # install dependancies and dev tools
    RUN apt-get update && apt-get install -y unzip zip nano net-tools curl

    # Simple Authenticator
    # unzip the auth plugin and remove zip
    RUN unzip $DEPLOY_DIR/authn.simple-$AUTH_VERSION-distro.zip -d $DEPLOY_DIR \
    && rm $DEPLOY_DIR/authn.simple-$AUTH_VERSION-distro.zip

    # Unpack the war file so we can copy in xml files
    RUN unzip $DEPLOY_DIR/authn.simple/authn.simple-$AUTH_VERSION.war -d $DEPLOY_DIR/authn.simple/unpacked
    RUN mv $DEPLOY_DIR/authn.simple/* $DEPLOY_DIR/ \
    && rm -r $DEPLOY_DIR/authn.simple/

    # put xml files into right place
    COPY simple/config/run.properties $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY simple/config/logback.xml $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY simple/config/web.xml $DEPLOY_DIR/unpacked/WEB-INF/ 

    # remove old war file and repackage/rename new one
    RUN rm -r $DEPLOY_DIR/authn.simple-$AUTH_VERSION.war \
    && cd $DEPLOY_DIR/unpacked \
    && zip -r authn.simple-$AUTH_VERSION.zip ./WEB-INF ./META-INF \
    && mv $DEPLOY_DIR/unpacked/authn.simple-$AUTH_VERSION.zip $DEPLOY_DIR/authn.simple-$AUTH_VERSION.war \
    && rm -r $DEPLOY_DIR/unpacked
    
    # Anonymous Authenticator
    # unzip the auth plugin and remove zip
    RUN unzip $DEPLOY_DIR/authn.anon-$AUTH_VERSION-distro.zip -d $DEPLOY_DIR \
    && rm $DEPLOY_DIR/authn.anon-$AUTH_VERSION-distro.zip
    
    # Unpack the war file so we can copy in xml files
    RUN unzip $DEPLOY_DIR/authn.anon/authn.anon-$AUTH_VERSION.war -d $DEPLOY_DIR/authn.anon/unpacked
    RUN mv $DEPLOY_DIR/authn.anon/* $DEPLOY_DIR/ \
    && rm -r $DEPLOY_DIR/authn.anon/

    # put xml files into right place
    COPY anon/config/run.properties $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY anon/config/logback.xml $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY anon/config/web.xml $DEPLOY_DIR/unpacked/WEB-INF/ 

    # remove old war file and repackage/rename new one
    RUN rm -r $DEPLOY_DIR/authn.anon-$AUTH_VERSION.war \
    && cd $DEPLOY_DIR/unpacked \
    && zip -r authn.anon-$AUTH_VERSION.zip ./WEB-INF ./META-INF \
    && mv $DEPLOY_DIR/unpacked/authn.anon-$AUTH_VERSION.zip $DEPLOY_DIR/authn.anon-$AUTH_VERSION.war \
    && rm -r $DEPLOY_DIR/unpacked

USER payara 
WORKDIR $HOME_DIR
