# Use the slim version of the Python 3.9 image as the base image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install -r requirements.txt

# Set the command to run when the container starts
CMD ["/bin/bash"]
