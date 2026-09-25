#!/bin/bash
# Pakai: ppro.sh file.jsx [timeout_detik]   atau   echo 'app.version' | ppro.sh - [timeout]
BR="$HOME/Library/Application Support/ClaudeBridge"; T="${2:-60}"
id="cmd_$(date +%s)_$$"
if [ "$1" = "-" ] || [ -z "$1" ]; then cat > "$BR/inbox/.$id.tmp"; else cp "$1" "$BR/inbox/.$id.tmp"; fi
mv "$BR/inbox/.$id.tmp" "$BR/inbox/$id.jsx"
for ((i=0;i<T*10;i++)); do
  if [ -f "$BR/outbox/$id.txt" ]; then cat "$BR/outbox/$id.txt"; rm -f "$BR/outbox/$id.txt"; echo; exit 0; fi
  sleep 0.1
done
rm -f "$BR/inbox/$id.jsx"; echo "TIMEOUT: bridge tidak merespon (panel Claude Bridge belum jalan?)" >&2; exit 1
