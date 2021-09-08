FROM python:3.9

RUN pip install gunicorn falcon

WORKDIR /app
COPY . .

EXPOSE 5678

CMD ["python", "-u", "server.py"]