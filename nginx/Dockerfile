FROM node:latest as build

WORKDIR /usr/local/app

COPY ./frontend/ /usr/local/app/

RUN npm install

RUN npm run build


FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY --from=build /usr/local/app/dist/frontend/ /src/
