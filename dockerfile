FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /opt/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /opt/

CMD ["./manage.py", "runserver", "0.0.0.0:8000"]