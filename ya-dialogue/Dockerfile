FROM python:3.8

RUN mkdir /app
WORKDIR /app

# Expose the port uWSGI will listen on
EXPOSE 40052

# Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# We copy the rest of the codebase into the image
COPY . .

ENV FLASK_APP=app

ENTRYPOINT uwsgi --ini uwsgi.ini