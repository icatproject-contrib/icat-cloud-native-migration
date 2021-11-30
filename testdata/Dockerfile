# This is the Dockerfile for the datagateway api script that 
# loads some test data into a DB, the db is set in the config
# file.

FROM python:3.6
WORKDIR /usr/src/app
COPY . .

# install everything thats needed to run the script
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/script
CMD [ "python3.6", "icat_db_generator.py", "-s 1", "-y 1"]