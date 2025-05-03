FROM python:3.10-slim

WORKDIR /app

COPY .env .env
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data

COPY code/ ./code/
COPY start.sh .

RUN chmod +x start.sh

EXPOSE 8000
EXPOSE 8502

CMD ["./start.sh"]
