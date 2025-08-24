#!/bin/bash

# --- KORRIGIERTES Aufräumskript für die Customer Mailing App ---

echo "🚀 Starte das Aufräumen der Projektstruktur (Version 2)..."

# Schritt 1: Definiere die Verzeichnisse
APP_DIR="app"
SRC_DIR="src"
SERVICES_TARGET="$APP_DIR/services"
IMPORTERS_TARGET="$SERVICES_TARGET/importers"
EXPORTERS_TARGET="$SERVICES_TARGET/exporters"

# Prüfe, ob das src-Verzeichnis existiert, bevor du startest
if [ ! -d "$SRC_DIR" ]; then
    echo "ℹ️  Das 'src'-Verzeichnis existiert nicht mehr. Das Aufräumen wurde möglicherweise schon abgeschlossen."
    exit 0
fi

# Schritt 2: Verschiebe die Importer-Dateien aus src/
echo "🚚 Verschiebe Importer-Module..."
mv "$SRC_DIR/csv_importer.py" "$IMPORTERS_TARGET/"
mv "$SRC_DIR/msg_importer.py" "$IMPORTERS_TARGET/"
mv "$SRC_DIR/vcf_importer.py" "$IMPORTERS_TARGET/"
mv "$SRC_DIR/xlsx_importer.py" "$IMPORTERS_TARGET/"

# Schritt 3: Verschiebe die Exporter-Dateien aus src/
echo "🚚 Verschiebe Exporter-Module..."
mv "$SRC_DIR/csv_exporter.py" "$EXPORTERS_TARGET/"
mv "$SRC_DIR/pdf_exporter.py" "$EXPORTERS_TARGET/"
mv "$SRC_DIR/xlsx_exporter.py" "$EXPORTERS_TARGET/"

# Schritt 4: Verschiebe und benenne die zentralen Service-Dateien aus src/
echo "🚚 Verschiebe und benenne zentrale Service-Dateien..."
mv "$SRC_DIR/importer.py" "$SERVICES_TARGET/importer_service.py"
mv "$SRC_DIR/exporter.py" "$SERVICES_TARGET/exporter_service.py"

# Schritt 5: Lösche die alte app.py und das jetzt leere src-Verzeichnis
echo "🗑️  Lösche alte Dateien und das 'src'-Verzeichnis..."
rm -f app.py
rm -rf "$SRC_DIR"

# Schritt 6: Lösche alle __pycache__ Ordner
echo "🧹 Säubere __pycache__ Verzeichnisse..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "✅ Aufräumen erfolgreich abgeschlossen!"
echo "➡️  Deine Projektstruktur ist jetzt sauber."
echo "➡️  Denke daran, die 'url_for()' Aufrufe in deinen Templates anzupassen!"