FROM python:3.6.3-jessie
MAINTAINER AsyncCeleryWebApp

RUN apt-get update && apt-get install -y \
        build-essential

WORKDIR /app

# Install Requirements
COPY requirements.txt /app
RUN pip3 install -U -r /app/requirements.txt

# Now do rest of work
COPY . /app

EXPOSE 8080

# using hug
CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:8080", "hug_handler:__hug_wsgi__"] 

#using aiohttp
# CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:8080", "request_handler:APP"]
