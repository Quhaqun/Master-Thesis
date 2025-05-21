#!/bin/bash

# Lokales Verzeichnis (anpassen!)
SRC="/home/deinuser/Master-Thesis/sv_upload_local/Data"

# Zielpfad in der tuBCloud (z. B. ein Ordner namens Thesis-Backup)
DEST="tubcloud:Master Thesis Data"

# Hochladen
rclone copy "$SRC" "$DEST" --log-file=/var/log/rclone-tubcloud.log --create-empty-src-dirs --verbose
