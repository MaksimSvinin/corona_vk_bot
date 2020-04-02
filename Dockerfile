FROM python:3.6

RUN pip install --upgrade pip && pip install pipenv

ARG APP_DIR=/corona_vk_bot
WORKDIR "$APP_DIR"

COPY Pipfile Pipfile.lock $APP_DIR/
RUN pipenv install --system

COPY . $APP_DIR/
