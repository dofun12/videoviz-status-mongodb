FROM python:3.11-alpine
WORKDIR /app

COPY requirements_all.txt requirements_all.txt
RUN pip3 install -r requirements_all.txt

COPY . .

CMD [ "python", "main.py"]