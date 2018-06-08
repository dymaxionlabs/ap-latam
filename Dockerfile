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
      python3-venv \
      virtualenv \
  && rm -rf /var/lib/apt/lists/*

# Configure locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
  && dpkg-reconfigure --frontend=noninteractive locales \
  && update-locale LANG=en_US.UTF-8 \

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install Poetry
RUN pip install -U poetry

# Install Python packages
COPY pyproject.toml pyproject.lock /app/
RUN poetry install --no-dev

ADD . /app/

ENV PYTHONPATH /app

ENTRYPOINT ["/app/docker/entrypoint.sh"]
