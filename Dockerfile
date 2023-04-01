FROM python:3.10-buster
ENV WORKDIR_PATH=/app
ENV DOCKER_RUNNING=Yes

# Set Workdir
WORKDIR ${WORKDIR_PATH}

# Copy requirements.txt and Makefile to WORKDIR
# Run and install all required modules for container
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy all files to WORKDIR
COPY . .

EXPOSE 8000

CMD ["python", "/app/main/main.py"]