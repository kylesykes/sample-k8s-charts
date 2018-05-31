FROM python:3.6.3-jessie
MAINTAINER AsyncCeleryBackend

RUN apt-get update && apt-get install -y \
    build-essential

WORKDIR /app

# Install Requirements
COPY requirements.txt /app
RUN pip3 install -U -r /app/requirements.txt

# Now do rest of work
COPY . /app

CMD [ "celery", "worker", "-A", "tasks", "-Q", "samplequeuename" ]