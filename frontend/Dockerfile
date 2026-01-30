# Build stage
FROM node:20-alpine as builder

WORKDIR /app

ARG VITE_API_URL=/api

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN VITE_API_URL=$VITE_API_URL npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html
RUN chmod -R a+r /usr/share/nginx/html

# Copy nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
