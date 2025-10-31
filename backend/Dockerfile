FROM python:3.9-slim

WORKDIR /app

# Install all system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file 
COPY requirements.txt . 

# Install Python dependencies 
RUN pip install --no-cache-dir -r requirements.txt 

# Copy application code 
COPY . . 

# Create directory for temporary files 
RUN mkdir -p /app/temp 

# Expoe port
EXPOSE 5000

# Set environment variables 
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# RUN the application
CMD ["python", "app.py"]




