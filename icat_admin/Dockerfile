FROM node:14-alpine AS development
ENV NODE_ENV development
# Add a work directory
WORKDIR /app
COPY package.json /app
COPY yarn.lock /app
RUN yarn install
COPY . /app
# Expose port
EXPOSE 8080
# Start the app
CMD [ "yarn", "dev" ]

# go to: http://localhost:8080/
# https://localhost:18181/icat/
# simple
# root
# pw
