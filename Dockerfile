FROM python:3.10-slim

WORKDIR /quiz_CI.ipynb

COPY req /quiz_CI.ipynb

RUN pip install --no-cache-dir -r requirements.txt

COPY . .