FROM python:3.9-slim-buster
COPY main.py /app/main.py
COPY utils.py /ap/putils.py
WORKDIR /app
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]