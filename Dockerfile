FROM python:3.12-slim

WORKDIR /home/piyush/app

COPY requirement.txt ./

RUN pip install --no-cache-dir -r requirement.txt

EXPOSE 5000

CMD["python","app.py"]

