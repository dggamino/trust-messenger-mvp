#!/data/data/com.termux/files/usr/bin/bash
# 🔐 Trust Messenger Auto-Sync Script by Dotcom

PROJECT_DIR="$HOME/trust_messenger"
BACKUP_DIR="$PROJECT_DIR/backup"
DATA_JSON="$PROJECT_DIR/data/trust_log.json"

cd "$PROJECT_DIR"

echo "📦 [$(date)] Iniciando sincronización..."

# 1️⃣ Exportar JSON actualizado (desde Python)
python3 trust_message.py > /dev/null 2>&1

# 2️⃣ Crear copia ZIP
ZIPFILE="$BACKUP_DIR/trust_$(date +%F_%H%M).zip"
zip -qr "$ZIPFILE" "$PROJECT_DIR"
echo "💾 Copia guardada en: $ZIPFILE"

# 3️⃣ Commit y push Git
git add data/trust_log.json
git commit -m "Auto-sync $(date '+%F %H:%M')" > /dev/null 2>&1
git push origin main

echo "🚀 Repositorio actualizado y Netlify se sincronizará automáticamente."
echo "✅ Finalizado a las $(date)"

