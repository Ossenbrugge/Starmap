#!/bin/sh
# If /app/data is a mounted volume without a built database (fresh host),
# assemble it from the JSON/CSV sources shipped in the image. The image also
# bakes a DB at build time, so plain `docker run` (no volume) starts instantly.
set -e

if [ ! -f /app/data/starmap.sqlite ]; then
    echo "No starmap.sqlite in /app/data — building from sources..."
    python scripts/migrate_to_sqlite.py
    python scripts/seed_star_canon.py
    python scripts/migrate_timeline_events.py
    python scripts/migrate_nation_lore.py
    python scripts/seed_saga_lore.py
    python scripts/seed_master_timeline.py
    python scripts/import_provinces.py
    echo "Database build complete."
fi

exec "$@"
