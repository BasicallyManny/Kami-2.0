FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Create proper directory structure for the module
RUN mkdir -p /app/frontend

# Copy the entire frontend directory to the working directory in the container
COPY ./frontend /app/frontend

# Make sure we have an __init__.py file
RUN touch /app/frontend/__init__.py

# Copy the requirements.txt file to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot with the correct module path
CMD ["python", "-m", "frontend.kami"]