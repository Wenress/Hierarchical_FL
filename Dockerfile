FROM python:3.10-slim
WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN apt-get update && apt-get install -y curl
RUN pip install -Ur requirements.txt
ENTRYPOINT ["python3"]
