FROM httpd:2.4

ADD https://github.com/ral-facilities/datagateway/releases/download/snapshot/datagateway-download-snapshot.tar.gz /tmp/

RUN tar -xvf /tmp/datagateway-download-snapshot.tar.gz --strip-components=1 -C /usr/local/apache2/htdocs/

WORKDIR /usr/local/apache2/htdocs/

RUN mkdir -p plugins/datagateway-download

COPY config/datagateway-download-settings.json /usr/local/apache2/htdocs/plugins/datagateway-download/

COPY config/httpd.conf /usr/local/apache2/conf/

RUN mv res plugins/datagateway-download

RUN sed -i -e 's,/plugins/datagateway-download,http://localhost:8082/plugins/datagateway-download,g' /usr/local/apache2/htdocs/main.js