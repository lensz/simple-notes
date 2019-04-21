FROM python:3.5-alpine

EXPOSE $SIMPE_NOTES_PORT

RUN mkdir /opt/simple-notes
WORKDIR /opt/simple-notes

COPY Pipfile.lock Pipfile ./
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY src ./src
COPY .env ./
CMD pipenv run python src/app.py