# Use an official Python base image
FROM python:3.11-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY . .

# Expose the port the application will run on
EXPOSE 8000