FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app_refactored.py

EXPOSE 8080

# Production WSGI server; app_refactored exposes `app` at module level.
# Workers=2/threads=4: the SQLite Database singleton is per-process and its
# lock serializes queries, so a couple of threaded workers is the sweet spot.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "60", "app_refactored:app"]
