FROM httpd:2.4

ADD https://github.com/ral-facilities/datagateway/releases/download/snapshot/datagateway-download-snapshot.tar.gz /tmp/
RUN tar -xvf /tmp/datagateway-download-snapshot.tar.gz --strip-components=1 -C /usr/local/apache2/htdocs/
