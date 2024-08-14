# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages
RUN pip install --no-cache-dir grpcio grpcio-tools

# Make port 5440 available to the world outside this container
EXPOSE 5440

# Run server.py when the container launches
CMD ["python", "server.py"]
