FROM --platform=linux/amd64 python:3.12-bullseye as build

WORKDIR /app

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1
# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

COPY . /app

RUN pip install -r requirements.txt

CMD ["python3", "main.py", "bash_linux_exams"]