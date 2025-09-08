# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user and required directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /tmp && \
    chown -R appuser:appuser /app /tmp

# Create startup script to handle service account credentials
COPY --chown=appuser:appuser startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

USER appuser

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start command
CMD ["/app/startup.sh"]
