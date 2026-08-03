# Stage 1: Build the Vite React application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package configuration and install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy frontend source code and build the production bundle
COPY . .
RUN npm run build

# Stage 2: Serve compiled web app with lightweight Nginx server
FROM nginx:alpine

# Copy custom Nginx proxy configuration if present, otherwise default to standard serving
COPY --from=build /app/dist /usr/share/nginx/html

# Create an Nginx configuration that proxies backend API requests to the FastAPI container
RUN echo 'server { \
    listen       80; \
    server_name  localhost; \
    root   /usr/share/nginx/html; \
    index  index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location ~ ^/(auth|ingest|search|chat|patients|audit|health)/ { \
        proxy_pass http://medintel_backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_buffering off; \
        proxy_read_timeout 300s; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
