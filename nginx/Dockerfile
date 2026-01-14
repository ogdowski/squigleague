# Nginx with versioned configuration
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/nginx.conf

# Copy production nginx config
COPY nginx.prod.conf /etc/nginx/nginx.conf

# Create certbot directories
RUN mkdir -p /var/www/certbot /etc/letsencrypt

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:80/health || exit 1
