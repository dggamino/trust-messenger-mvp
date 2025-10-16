#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trust Messenger Bot v1.3 🔐
Telegram bot para registrar, listar y calcular reputación de compromisos personales o comunitarios.
Compatible con Android 14 + Termux + Python 3.12
"""

import os, sqlite3, time, hashlib, json, asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# ========================
# CONFIGURACIÓN DE RUTAS
# ========================

BASE_DIR = Path.home() / "trust_messenger"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "trust.db"
JSON_PATH = DATA_DIR / "trust_log.json"
ENV_PATH = DATA_DIR / ".env"

# ========================
# CARGA DEL TOKEN
# ========================

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    raise FileNotFoundError("❌ Archivo .env no encontrado en data/.env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("⚠️ No se encontró TELEGRAM_TOKEN en data/.env")

# ========================
# FUNCIONES DE BASE DE DATOS
# ========================

def init_db():
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

def add_commitment(user, message, amount, due_date):
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
    return h

def calc_reputation(user):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT status FROM commitments WHERE user=?", (user,))
    rows = cur.fetchall()
    con.close()
    if not rows: return 0
    total = len(rows)
    done = sum(1 for r in rows if r[0] == "COMPLETED")
    return round((done / total) * 100, 2)

def list_commitments(user):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    SELECT message, amount, due_date, status, hash
    FROM commitments WHERE user=?
    ORDER BY timestamp DESC
    """, (user,))
    rows = cur.fetchall()
    con.close()
    return rows

# ========================
# COMANDOS DEL BOT
# ========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Trust Messenger* 🔐\n\n"
        "Comandos disponibles:\n"
        "/add mensaje | monto | fecha → Registrar compromiso\n"
        "/rep → Ver reputación actual\n"
        "/list → Listar todos tus compromisos\n",
        parse_mode="Markdown"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/add", "", 1).strip()
    if "|" not in text:
        await update.message.reply_text("Formato inválido. Usa:\n/add mensaje | monto | fecha")
        return
    try:
        message, amount, due = [x.strip() for x in text.split("|")]
        h = add_commitment(update.effective_user.first_name, message, float(amount), due)
        await update.message.reply_text(f"📝 Compromiso registrado con hash `{h[:10]}...`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def rep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    score = calc_reputation(user)
    await update.message.reply_text(f"📊 Tu reputación actual es *{score}%*", parse_mode="Markdown")

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    rows = list_commitments(user)
    if not rows:
        await update.message.reply_text("⚠️ No tienes compromisos registrados aún.")
        return
    msg = f"📋 *Compromisos de {user}:*\n\n"
    for r in rows[:10]:  # muestra los 10 más recientes
        msg += f"• {r[0]} — 💰 {r[1]} — ⏰ {r[2]} — [{r[3]}]\nHash: `{r[4][:10]}...`\n\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ========================
# MAIN LOOP MODO ESTABLE
# ========================

if __name__ == "__main__":
    init_db()

    async def runner():
        print("🤖 Bot Trust Messenger corriendo (v1.3 estable con /list)...")
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("add", add))
        app.add_handler(CommandHandler("rep", rep))
        app.add_handler(CommandHandler("list", list_cmd))
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("\n🛑 Cerrando bot...")
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

    asyncio.run(runner())

