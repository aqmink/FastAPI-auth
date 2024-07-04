FROM python:3.11.9

RUN mkdir fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /fastapi_app/docker/*.sh