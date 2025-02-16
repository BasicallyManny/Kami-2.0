# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set work directory to the root of the app
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container's work directory
COPY . /app

# Run the Discord bot using "python -m frontend.kami"
CMD ["python", "-m", "frontend.kami"]

