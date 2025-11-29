FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for Pillow or other libs)
# Install system dependencies (curl is required for scraping)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port (Railway will override this, but good for documentation)
EXPOSE 3000

# Command to run the application
# Using gunicorn to serve the Flask app
CMD ["gunicorn", "api.index:app", "--bind", "0.0.0.0:3000", "--timeout", "120"]
