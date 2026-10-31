FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --system --create-home --uid 10001 botuser \
    && mkdir -p /app/data && chown botuser /app/data
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY core core
COPY providers providers
COPY cogs cogs

USER botuser
CMD ["python", "bot.py"]
