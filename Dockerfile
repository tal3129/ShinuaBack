# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Download and install wkhtmltopdf
RUN apt-get update && apt-get install -y wget && \
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb && \
    dpkg -i wkhtmltox_0.12.6-1.buster_amd64.deb || apt-get install -y --fix-broken && \
    rm -rf wkhtmltox_0.12.6-1.buster_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Copy the requirements.txt file to the container
COPY backend/requirements.txt backend/requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend source code to the container
COPY . .

# Install the backend module
RUN pip install -e .


# Expose port 8000 for the FastAPI server
EXPOSE 8000

WORKDIR /app/backend

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--root-path", "/api"]
