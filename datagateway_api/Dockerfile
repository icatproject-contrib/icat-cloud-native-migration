# This is the Dockerfile for the datgateway_api container

FROM python:3.8

# install dependancies
RUN pip install poetry
RUN apt-get update && apt-get install -y unzip

WORKDIR /app

# get the repo
ADD https://github.com/ral-facilities/datagateway-api/archive/refs/tags/v8.0.0.zip /app

# unzip and remove top level folder
RUN unzip /app/v8.0.0.zip -d ./tmp
RUN mv ./tmp/*/* .

RUN poetry run pip uninstall -y setuptools
RUN poetry run pip install 'setuptools<58.0.0'
RUN poetry install

# copy the config across
COPY config/config.yaml /app/datagateway_api/

# set the app running
#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["poetry","run","python3", "-m", "datagateway_api.src.main"]