# Use a lightweight Python image as the base
FROM python:3.11-slim AS base

# Set environment variables for Flask and Python
ENV FLASK_ENV=production \
    FLASK_APP=app.py \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Copy and install dependencies
COPY /app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Install Gunicorn WSGI server
RUN pip install --no-cache-dir gunicorn

# Copy world-readable flag file and set permissions
COPY flag.txt /flag.txt
RUN chmod 444 /flag.txt

# Copy the application code
COPY /app /app

# Create a directory for handouts (empty but needs to exist)
RUN mkdir /handout

# Expose the intended port
EXPOSE 8080

ENV OPENAI_API_KEY="<censored>"

# Define the command to run the app with Gunicorn as a WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "8", "--chdir", "/app", "app:app"]
