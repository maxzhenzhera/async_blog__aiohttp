from python:3.9.4-slim


# set work dir
WORKDIR /app

# vim installation [for debug-editing purposes]
#RUN apt-get update -y
#RUN apt-get install vim -y

# prepare environment [copy dependencies files, install all dependencies]
COPY requirements.txt Pipfile Pipfile.lock .
RUN pip install pipenv
RUN pipenv install --system --deploy

# copy all project
COPY . .

# set command for running
CMD ["python", "core/__main__.py"]