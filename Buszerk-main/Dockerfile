FROM python:3.9 AS builder

# Set working directory
WORKDIR /app

# Copy only requirements.txt to leverage cache
COPY requirements.txt /app/

# Upgrade pip and install dependencies with a different mirror and increased timeout
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --index-url https://pypi.doubanio.com/simple --default-timeout=100 -r requirements.txt

# Final stage
FROM python:3.9

# Set working directory
WORKDIR /app

# Install Git for commit info
RUN apt-get update && apt-get install -y git

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

# Copy the rest of the application
COPY . /app

# Command to run the app
CMD ["python", "app.py"]