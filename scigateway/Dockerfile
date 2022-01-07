
FROM node:14-alpine AS development
ENV NODE_ENV development
# Add a work directory
WORKDIR /app
# Cache and Install dependencies
# install app 
ADD https://github.com/ral-facilities/scigateway/archive/refs/heads/master.zip ./
RUN unzip /app/master.zip -d ./tmp
RUN mv ./tmp/*/* .
RUN yarn install
# Copy setting files across
COPY config/settings.json /app/public/
# Expose port
EXPOSE 3000
# Start the app
CMD [ "yarn", "start" ]
