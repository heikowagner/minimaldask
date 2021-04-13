FROM python:3.9.2-alpine3.13

MAINTAINER Heiko Wagner, heikowagner@thebigdatablog.com

RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --update --no-cache py3-numpy py3-pandas@testing
RUN mv -f /usr/lib/python3.8/site-packages/* /usr/local/lib/python3.9/site-packages/

RUN echo "INSTALLING DASK"
RUN apk update \
    && apk add --virtual build-deps gcc musl-dev linux-headers libffi-dev jpeg-dev zlib-dev libjpeg g++ build-base libzmq zeromq-dev\
    && apk add py-psutil libjpeg\
    && pip install dask[complete] jupyter-server-proxy \
    && apk del build-deps \
    && pip cache purge \
	&& find /usr/local/lib/python3.9/site-packages -follow -type f -name '*.a' -delete \
    && find /usr/local/lib/python3.9/site-packages -follow -type f -name '*.pyc' -delete \
    && find /usr/local/lib/python3.9/site-packages -follow -type f -name '*.js.map' -delete \
    && find /usr/local/lib/python3.9/site-packages/bokeh/server/static -follow -type f -name '*.js' ! -name '*.min.js' -delete

RUN echo "COPY ENTRYPOINT"
COPY entrypoint.sh /usr/local/bin
RUN chmod 755 /usr/local/bin/entrypoint.sh

#Just in case entrypoint.sh was edited using Windows
RUN apk add dos2unix --update-cache --repository http://dl-3.alpinelinux.org/alpine/edge/community/ --allow-untrusted \
	&& dos2unix /usr/local/bin/entrypoint.sh \
	&& apk del dos2unix

ENTRYPOINT ["entrypoint.sh"]