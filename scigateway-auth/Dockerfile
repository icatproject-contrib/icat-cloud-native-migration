# This is the Dockerfile for the Scigateway_auth container

FROM python:3.7

# install dependancies
RUN pip install poetry
RUN apt-get update && apt-get install -y unzip openssh-client

WORKDIR /app

# make dir to hold keys
RUN mkdir keys

# get the repo
ADD https://github.com/ral-facilities/scigateway-auth/archive/refs/heads/master.zip /app

# unzip and remove top level folder
RUN unzip /app/master.zip -d ./tmp
RUN mv ./tmp/*/* .

# install app dependancies
RUN poetry config virtualenvs.create false
RUN poetry install
RUN ssh-keygen -q -t rsa -m 'PEM' -N '' -f keys/jwt-key

# copy the config across
COPY config/config.json /app/scigateway_auth/

# set the app running
#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["python3", "-m", "scigateway_auth.app"]