FROM nginx:1.27-alpine

ENV SAFEVIEW_API_BASE=/api
ENV SAFEVIEW_API_UPSTREAM=http://safeview-api:8000

COPY index.html styles.css app.js config.js /usr/share/nginx/html/
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.d/40-safeview-config.sh /docker-entrypoint.d/40-safeview-config.sh

EXPOSE 80
