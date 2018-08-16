FROM tensorflow/tensorflow:latest-gpu-py3

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      gdal-bin \
      libgdal-dev \
      libproj-dev \
      libspatialindex-dev \
      locales \
  && rm -rf /var/lib/apt/lists/*

# Configure locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
  && dpkg-reconfigure --frontend=noninteractive locales \
  && update-locale LANG=en_US.UTF-8

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install Python packages
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

ADD . /app/

ENV PYTHONPATH /app

ENTRYPOINT ["/app/docker/entrypoint.sh"]
