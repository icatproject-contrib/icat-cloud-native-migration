# This is the Dockerfile for the lucene service which is needed to run icat.
# The Dockerfile can be run on its own or can be ran as part of a Docker 
# Compose suite of containers. The run.properties contains the list of
# allowed ip address which can connect to this service.

# Based on JDK8, also an option for JDK11
FROM payara/server-full:5.2021.7

# Define variables to use later on in this dockerfile. 
ARG LUCENE_VERSION=1.1.0

# Download the contents into the servers deployment directory.
ADD https://repo.icatproject.org/repo/org/icatproject/icat.lucene/$LUCENE_VERSION/icat.lucene-$LUCENE_VERSION-distro.zip $DEPLOY_DIR/

RUN mkdir -p ~/data/lucene

# switch to root user and preform sudo actions for the Lucene service
USER root

    # install dependancies and dev tools
    RUN apt-get update && apt-get install -y unzip zip nano net-tools curl

    # unzip the ids and remove zip
    RUN unzip $DEPLOY_DIR/icat.lucene-$LUCENE_VERSION-distro.zip -d $DEPLOY_DIR \
    && rm $DEPLOY_DIR/icat.lucene-$LUCENE_VERSION-distro.zip

    # Unpack the war file so we can copy in xml files
    RUN unzip $DEPLOY_DIR/icat.lucene/icat.lucene-$LUCENE_VERSION.war -d $DEPLOY_DIR/icat.lucene/unpacked
    RUN mv $DEPLOY_DIR/icat.lucene/* $DEPLOY_DIR/ \
    && rm -r $DEPLOY_DIR/icat.lucene

    # put xml files into right place
    COPY config/run.properties $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY config/logback.xml $DEPLOY_DIR/unpacked/WEB-INF/classes/
    COPY config/web.xml $DEPLOY_DIR/unpacked/WEB-INF/ 

    # remove old war file and repackage/rename new one
    RUN rm -r $DEPLOY_DIR/icat.lucene-$LUCENE_VERSION.war \
    && cd $DEPLOY_DIR/unpacked \
    && zip -r icat.lucene-$LUCENE_VERSION.zip ./WEB-INF ./META-INF \
    && mv $DEPLOY_DIR/unpacked/icat.lucene-$LUCENE_VERSION.zip $DEPLOY_DIR/icat.lucene-$LUCENE_VERSION.war \
    && rm -r $DEPLOY_DIR/unpacked

USER payara
    
WORKDIR $HOME_DIR