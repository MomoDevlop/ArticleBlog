FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 4000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "4000"]
