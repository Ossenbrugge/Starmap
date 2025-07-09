#!/bin/bash

# Migration script to convert Starmap data to MontyDB
# This script will backup existing data and run the migration

echo "🚀 Starting Starmap MontyDB Migration"
echo "====================================="

# Create backup directory
BACKUP_DIR="./backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup of existing data..."
cp *.csv "$BACKUP_DIR/" 2>/dev/null || echo "No CSV files to backup"
cp *.json "$BACKUP_DIR/" 2>/dev/null || echo "No JSON files to backup"
cp *.py "$BACKUP_DIR/" 2>/dev/null || echo "No Python data files to backup"

echo "✅ Backup created in: $BACKUP_DIR"

# Install MontyDB if not already installed
echo "📚 Installing MontyDB..."
pip install montydb==2.5.3

# Run the migration
echo "🔄 Running data migration..."
cd database
python migrate.py

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
    echo ""
    echo "📊 Database created at: ./starmap_db"
    echo "🎉 You can now run the application with MontyDB!"
    echo ""
    echo "Next steps:"
    echo "1. Run 'python app.py' to start the application"
    echo "2. Visit http://localhost:8080 to view the starmap"
    echo "3. Test the new database features"
else
    echo "❌ Migration failed!"
    echo "Please check the error messages above."
    exit 1
fi

echo "====================================="
echo "🏁 Migration process complete"