# Use an official Python runtime as a parent image
# python:3.11-slim is a good, lightweight choice
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
# By copying and installing requirements first, Docker can cache this layer,
# speeding up future builds if your dependencies don't change.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your server code into the container
COPY server.py .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define the command to run your app.
# This tells uvicorn to run the 'starlette_app' object from your 'server.py' file.
# It listens on all network interfaces (0.0.0.0) on port 8080.
CMD ["uvicorn", "server:starlette_app", "--host", "0.0.0.0", "--port", "8080"]