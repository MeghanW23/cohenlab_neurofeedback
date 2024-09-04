# Use Python 3.10.10 Slim image as base
FROM python:3.10.10-slim-bullseye

# Set the working directory in the container
WORKDIR /working_dir

# Install Git and other necessary packages
RUN apt-get update && \
    apt-get install -y git

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh

# Make the script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint to your script
ENTRYPOINT ["/app/entrypoint.sh"]

# Install any required packages
RUN pip install --no-cache-dir -r requirements.txt

