FROM python:3.8

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG DJANGO_ENV=production


ENV DJANGO_ENV=${DJANGO_ENV} \
    # python:
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # app:
    HOME=/app \
    APP_HOME=/app/src

EXPOSE 8000

SHELL ["/bin/bash", "-c"]

# Postresql repository
RUN apt-get update && apt-get install -y gnupg2 lsb-release && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee  /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && apt-get install -y \
    gettext netcat nano postgresql-client-12 && \
    apt-get clean && \
    \
    addgroup --gid $GROUP_ID user && \
    adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user && \
    \
    mkdir /app && \
    mkdir -p /app/runtime/logs && \
    chown user:user -R /app

ENV PATH="/home/user/.local/bin:${PATH}"
ENV PATH="/app/.local/bin:${PATH}"

WORKDIR $APP_HOME

USER user

COPY --chown=user:user ./src/requirements/base.txt $APP_HOME/requirements/
COPY --chown=user:user ./src/requirements/production.txt $APP_HOME/requirements/
COPY --chown=user:user ./src/requirements/local.txt $APP_HOME/requirements/

# if development
RUN  if [ "$DJANGO_ENV" = 'development' ] || [ "$DJANGO_ENV" = 'test' ]; then \
    python -m pip install --upgrade pip && \
    pip install -r requirements/local.txt; \
else \
    python -m pip install --upgrade pip && \
    pip install -r requirements/production.txt; \
fi

COPY --chown=user:user ./src/ $APP_HOME
COPY --chown=user:user ./docker/app/entrypoint.sh $HOME/entrypoint.sh
COPY --chown=user:user ./docker/app/celery_entrypoint.sh $HOME/celery_entrypoint.sh
COPY --chown=user:user ./docker/app/bashrc $HOME/.bashrc

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
