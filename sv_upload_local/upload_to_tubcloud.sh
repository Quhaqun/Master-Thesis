#!/bin/bash

# Lokales Verzeichnis
SRC="$HOME/Master-Thesis/sv_upload_local/Data"

# Zielverzeichnis auf tuBCloud (z. B. "Master Thesis Data" – anpassen, falls du etwas anderes willst)
DEST="tubcloud:Master Thesis Data"

# Log-Datei (optional)
LOGFILE="$HOME/Master-Thesis/sv_upload_local/rclone_upload.log"

# Upload ausführen
rclone copy "$SRC" "$DEST" --log-file="$LOGFILE" --create-empty-src-dirs --verbose
