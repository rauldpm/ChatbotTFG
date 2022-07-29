FROM nginx:1.18.0

# copy over static assets for https connections
COPY Docker/nginx/certs/* /etc/letsencrypt/live/your-ld-domain/

# copy custom entrypoint
COPY Docker/nginx/conf/nginx-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh

# copy custom nginx config
RUN rm /etc/nginx/conf.d/default.conf
COPY Docker/nginx/conf/default.conf /etc/nginx/conf.d/
COPY Docker/nginx/conf/servers /etc/nginx/

# nginx init
RUN ["chmod", "+x", "/usr/local/bin/nginx-entrypoint.sh"]
ENTRYPOINT ["/usr/local/bin/nginx-entrypoint.sh"]
