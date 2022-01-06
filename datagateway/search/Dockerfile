FROM httpd:2.4

ADD https://github.com/ral-facilities/datagateway/releases/download/snapshot/datagateway-search-snapshot.tar.gz /tmp/
RUN tar -xvf /tmp/datagateway-search-snapshot.tar.gz --strip-components=1 -C /usr/local/apache2/htdocs/
COPY config/datagateway-search-settings.json /usr/local/apache2/htdocs/
WORKDIR /usr/local/apache2/htdocs/
RUN mkdir -p plugins/datagateway-search
RUN mv res plugins/datagateway-search