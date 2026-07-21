FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

FROM base AS development
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD ["/app/entrypoint.sh"]

FROM base AS production
CMD ["/app/entrypoint.sh"]
