FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y 
spamassassin spamc python3 python3-pip curl ca-certificates 
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 10000

CMD ["/app/start.sh"]
