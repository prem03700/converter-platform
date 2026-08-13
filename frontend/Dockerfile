# ─── Stage 1: Build ────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --quiet
COPY . .

# Bake the API URL into the build (uses relative path by default so
# nginx can proxy /api to the backend — change only for non-Docker deploys)
ARG VITE_API_URL=/api/v1
ARG VITE_MAX_UPLOAD_MB=200
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_MAX_UPLOAD_MB=${VITE_MAX_UPLOAD_MB}

RUN npm run build

# ─── Stage 2: Serve static files ────────────────────────────────────────────
FROM nginx:1.25-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# SPA routing: send all non-asset requests to index.html so React Router works
RUN printf 'server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  location / {\n\
    try_files $uri $uri/ /index.html;\n\
  }\n\
  location ~* \\.(js|css|png|jpg|svg|ico|woff2)$ {\n\
    expires 1y;\n\
    add_header Cache-Control "public, immutable";\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
