FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source
COPY src/ src/

EXPOSE 8000
CMD ["uvicorn", "src.backend.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
