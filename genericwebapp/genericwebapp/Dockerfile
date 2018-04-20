FROM python:3.6.3-jessie
MAINTAINER GenericWebApp

RUN apt-get update && apt-get install -y \
        build-essential

WORKDIR /app

# Install Requirements
COPY requirements.txt /app
RUN pip3 install -U -r /app/requirements.txt

# Now do rest of work
COPY . /app

EXPOSE 8080

CMD ["gunicorn", "-w", "3", "--bind", "0.0.0.0:8080", "views:app"]
