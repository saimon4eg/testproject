FROM python:3.13-slim-bullseye

RUN apt-get update \
    && apt-get -y install --no-install-recommends tini \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && mkdir -p /srv/testproject/backend \
    && useradd testuser --shell /bin/bash --no-create-home \
    && chown -R testuser:testuser /srv/testproject/backend

WORKDIR /srv/testproject/backend

RUN export PYTHONPATH=$PYTHONPATH:/srv/testproject/backend

COPY ./start.sh ./
COPY ./setup.py ./
COPY ./pyproject.toml ./
COPY ./alembic.ini ./

RUN pip install -e ./

USER testuser

ENTRYPOINT ["tini", "--"]
CMD ["/bin/bash", "./start.sh"]
