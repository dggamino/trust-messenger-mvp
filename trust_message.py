#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trust Messenger — versión corregida para Termux Android 14
Crea base local SQLite + registro de compromisos + exportación JSON
Autor: Dotcom 🔐
"""

import os, json, time, sqlite3, hashlib
from pathlib import Path

# ========================
# CONFIGURACIÓN SEGURA
# ========================

# Detecta home de Termux (siempre existe)
HOME = Path.home()

# Carpeta base del proyecto
BASE_DIR = HOME / "trust_messenger"

# Subcarpeta de datos (se crea si no existe)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Archivo SQLite y export JSON
DB_PATH = DATA_DIR / "trust.db"
JSON_PATH = DATA_DIR / "trust_log.json"


# ========================
# FUNCIONES PRINCIPALES
# ========================

def init_db():
    """Inicializa base SQLite"""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS commitments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            message TEXT,
            amount REAL,
            due_date TEXT,
            timestamp INTEGER,
            status TEXT,
            hash TEXT
        )
    """)
    con.commit()
    con.close()
    print("✅ Base de datos inicializada en:", DB_PATH)


def add_commitment(user, message, amount, due_date):
    """Registra nuevo compromiso"""
    data = f"{user}|{message}|{amount}|{due_date}|{time.time()}"
    h = hashlib.sha256(data.encode()).hexdigest()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO commitments (user,message,amount,due_date,timestamp,status,hash)
        VALUES (?,?,?,?,?,?,?)
    """, (user, message, amount, due_date, int(time.time()), "PENDING", h))
    con.commit()
    con.close()
    print(f"📝 Compromiso guardado para {user} con hash {h[:12]}...")
    return h


def mark_complete(hash_value):
    """Marca un compromiso como cumplido"""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE commitments SET status='COMPLETED' WHERE hash=?", (hash_value,))
    con.commit()
    con.close()
    print("✅ Compromiso completado:", hash_value[:12])


def calc_reputation(user):
    """Calcula reputación (cumplimiento %)"""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT status FROM commitments WHERE user=?", (user,))
    rows = cur.fetchall()
    con.close()
    if not rows:
        return 0
    total = len(rows)
    done = sum(1 for r in rows if r[0] == "COMPLETED")
    score = round((done / total) * 100, 2)
    print(f"📊 Reputación de {user}: {score}%")
    return score


def export_to_json():
    """Exporta los registros a JSON"""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT user,message,amount,due_date,status,hash FROM commitments")
    rows = cur.fetchall()
    con.close()

    out = [
        {
            "user": r[0],
            "message": r[1],
            "amount": r[2],
            "due_date": r[3],
            "status": r[4],
            "hash": r[5]
        } for r in rows
    ]

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("📤 Datos exportados a JSON:", JSON_PATH)
    return out


# ========================
# DEMO / PRUEBA LOCAL
# ========================

if __name__ == "__main__":
    init_db()
    h = add_commitment("Carlos", "Aportar al fondo familiar", 500, "2025-10-20")
    mark_complete(h)
    calc_reputation("Carlos")
    export_to_json()
    print("🏁 Ejecución completada correctamente.")
