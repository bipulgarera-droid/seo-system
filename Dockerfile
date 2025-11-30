FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for Pillow or other libs)
# RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port (Railway will override this, but good for documentation)
EXPOSE 3000

# Command to run the application
# Using gunicorn to serve the Flask app
# Use sh -c to allow environment variable expansion for PORT
CMD ["sh", "-c", "gunicorn api.index:app --bind 0.0.0.0:${PORT:-3000} --timeout 120"]
