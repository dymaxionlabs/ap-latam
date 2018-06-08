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
  && rm -rf /var/lib/apt/lists/*

RUN pip install -U poetry

COPY pyproject.toml pyproject.lock /app/
RUN poetry install --no-dev

ADD . /app/

ENV PYTHONPATH /app

ENTRYPOINT ["/app/docker/entrypoint.sh"]
