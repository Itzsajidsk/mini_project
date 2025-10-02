FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage layer caching
COPY requirements.txt ./
# Ensure packaging/build tools are recent to avoid build backend errors
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

ENV PORT 5000
EXPOSE $PORT

# Use shell form so $PORT is expanded at runtime by the container environment
CMD gunicorn -b 0.0.0.0:$PORT app:app
