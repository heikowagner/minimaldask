FROM python:3.9.2-alpine3.13

MAINTAINER Heiko Wagner, heikowagner@thebigdatablog.com

RUN echo "INSTALLING DASK"

ENTRYPOINT ["entrypoint.sh"]