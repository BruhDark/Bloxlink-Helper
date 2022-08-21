FROM python:3.10.5

WORKDIR /helper-bot

COPY requirements.txt .
COPY src ./

RUN pip install -r requirements.txt
RUN python ./src/main.py