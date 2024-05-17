FROM --platform=linux/amd64 python:3.12-bullseye as build

WORKDIR /app

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1
# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

COPY . /app

RUN pip install -r requirements.txt

# Accept the build argument EXAM_TYPE
ARG EXAM_TYPE
ARG EXAM_FOLDER


# Set a default value for EXAM_TYPE in case it's not provided
ENV EXAM_TYPE=${EXAM_TYPE:-bash_linux_exam}

ENV EXAM_FOLDER=${EXAM_FOLDER:-bash_linux_exam}


# Use shell form to ensure the environment variable is expanded
CMD python3 main.py --type $EXAM_TYPE $EXAM_FOLDER
