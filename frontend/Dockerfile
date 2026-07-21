FROM node:20-alpine
RUN npm install -g serve
WORKDIR /app
COPY build/web ./build/web
EXPOSE 8080
CMD ["sh", "-c", "serve -s build/web -l $PORT"]