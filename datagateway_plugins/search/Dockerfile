FROM httpd:2.4

ADD https://github.com/ral-facilities/datagateway/releases/download/snapshot/datagateway-search-snapshot.tar.gz /tmp/

RUN tar -xvf /tmp/datagateway-search-snapshot.tar.gz --strip-components=1 -C /usr/local/apache2/htdocs/

WORKDIR /usr/local/apache2/htdocs/

RUN mkdir -p plugins/datagateway-search

COPY config/datagateway-search-settings.json /usr/local/apache2/htdocs/plugins/datagateway-search/

COPY config/httpd.conf /usr/local/apache2/conf/

RUN mv res plugins/datagateway-search

RUN sed -i -e 's,/plugins/datagateway-search,http://localhost:8083/plugins/datagateway-search,g' /usr/local/apache2/htdocs/main.js
