FROM python:3.10-slim
WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN apt-get update && apt-get install -y curl 
RUN apt-get install -y --no-install-recommends docker.io 
RUN rm -rf /var/lib/apt/lists/*
RUN pip install -Ur requirements.txt
#ENTRYPOINT ["python3"]
ENTRYPOINT ["bash"]
