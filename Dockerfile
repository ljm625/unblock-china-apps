FROM ubuntu:18.10
MAINTAINER Jiaming Li <ljm625@gmail.com>
ENV NGINX_VERSION 1.9.11-1~jessie
RUN apt-get update
RUN apt-get install -y ca-certificates nginx gettext-base vim supervisor python3.6 python3.6-dev python3-pip libyaml-dev build-essential chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev
# Do phantomjs
RUN apt-get install -y wget
RUN cd ~
ENV PHANTOM_JS phantomjs-2.1.1-linux-x86_64
RUN wget https://github.com/Medium/phantomjs/releases/download/v2.1.1/$PHANTOM_JS.tar.bz2
RUN tar xvjf $PHANTOM_JS.tar.bz2
RUN mv $PHANTOM_JS /usr/local/share
RUN ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
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
RUN pip3 install -r /app/requirements.txt
EXPOSE 9000 9090 53
WORKDIR /app
RUN export LANG=C.UTF-8
CMD ["/usr/bin/supervisord"]
