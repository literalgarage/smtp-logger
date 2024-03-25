FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the packages with pip
RUN pip install '.'

ENTRYPOINT ["smtp-logger"]
