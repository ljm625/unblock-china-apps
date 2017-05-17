FROM ubuntu:14.04
MAINTAINER Jiaming Li <ljm625@gmail.com>
ENV NGINX_VERSION 1.9.11-1~jessie
RUN apt-get update
RUN apt-get install -y ca-certificates nginx gettext-base vim supervisor python-pip
# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log
# Make NGINX run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/
# Install Supervisord
RUN rm -rf /var/lib/apt/lists/*
# Custom Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/conf.d/
COPY ./ /app
RUN pip install -r /app/requirements.txt
EXPOSE 9000 9090
WORKDIR /app
RUN export LANG=C.UTF-8
CMD ["/usr/bin/supervisord"]
