FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# data/starmap.sqlite is gitignored; build it from the JSON/CSV sources,
# then layer on the saga canon (events, ownership, lore, provinces)
RUN python scripts/migrate_to_sqlite.py && \
    python scripts/seed_star_canon.py && \
    python scripts/migrate_timeline_events.py && \
    python scripts/migrate_nation_lore.py && \
    python scripts/seed_saga_lore.py && \
    python scripts/seed_master_timeline.py && \
    python scripts/import_provinces.py

ENV FLASK_APP=app_refactored.py

EXPOSE 8080

# Rebuilds the DB at container start when /app/data is a fresh mounted volume
# (a bind mount shadows the DB baked in above)
ENTRYPOINT ["/app/docker-entrypoint.sh"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=4); sys.exit(0 if r.status==200 else 1)"

# Production WSGI server; app_refactored exposes `app` at module level.
# Workers=2/threads=4: the SQLite Database singleton is per-process and its
# lock serializes queries, so a couple of threaded workers is the sweet spot.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "60", "app_refactored:app"]
