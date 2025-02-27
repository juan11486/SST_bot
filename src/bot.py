import os
import logging
import sqlite3
import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Cargar las variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "turnos.db"

# Verificar si el token se cargó correctamente
if not TOKEN:
    raise ValueError("⚠️ ERROR: No se encontró el token del bot en las variables de entorno. Verifica tu archivo .env")

# Función para manejar el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('¡Hola! Soy tu bot. ¿En qué puedo ayudarte?')

""" # Función para manejar mensajes de texto
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    await update.message.reply_text(f'Dijiste: {user_text}') """
    
# 🔹 Función para obtener los turnos desde la base de datos
def obtener_turnos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    hoy = datetime.date.today()
    cursor.execute("SELECT * FROM turnos")
    turnos = cursor.fetchall()
    
    conn.close()

    # Convertir datos a una lista de diccionarios
    cronograma = []
    for turno in turnos:
        cronograma.append({
            "turno": turno[0],
            "nombre": turno[1],
            "inicio": datetime.datetime.strptime(turno[2], "%d/%m/%Y").date(),
            "fin": datetime.datetime.strptime(turno[3], "%d/%m/%Y").date()
        })

    for i, turno in enumerate(cronograma):
        if turno["inicio"] <= hoy <= turno["fin"]:
            turno_actual = turno
            turno_pasado = cronograma[i - 1] if i > 0 else None
            turno_siguiente = cronograma[i + 1] if i + 1 < len(cronograma) else None
            return turno_pasado, turno_actual, turno_siguiente

    return None, None, None

# 🔹 Función para mostrar el botón "On-Call 🚨"
async def mostrar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("On-Call 🚨", callback_data="on_call")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Presiona el botón para ver los turnos:", reply_markup=reply_markup)

# 🔹 Función que responde cuando se presiona el botón "On-Call 🚨"
async def on_call(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    turno_pasado, turno_actual, turno_siguiente = obtener_turnos()

    mensaje = "🚨📢🚨 *Turnos On-Call:*\n"
    if turno_pasado:
        mensaje += f"\n🟢 *Turno Pasado:* {turno_pasado['nombre']} ({turno_pasado['inicio']} - {turno_pasado['fin']})"
    if turno_actual:
        mensaje += f"\n🔴👨‍🔧 *Turno Actual:* {turno_actual['nombre']} ({turno_actual['inicio']} - {turno_actual['fin']})"
    if turno_siguiente:
        mensaje += f"\n🟡 *Turno Siguiente:* {turno_siguiente['nombre']} ({turno_siguiente['inicio']} - {turno_siguiente['fin']})"

    await query.message.reply_text(mensaje, parse_mode="Markdown")

# Función principal
def main():
    logger.info("Iniciando el bot...")
    
    application = Application.builder().token(TOKEN).build()
    
    # Registrar comandos
    application.add_handler(CommandHandler("start", mostrar_boton))
    application.add_handler(CallbackQueryHandler(on_call, pattern="on_call"))
    
    logger.info("🤖 Bot en ejecución... Esperando mensajes")
    application.run_polling()
    
"""     # Reemplaza 'TU_TOKEN' con el token que te dio BotFather
    application = Application.builder().token(TOKEN).build()

    # Registra el manejador para el comando /start
    application.add_handler(CommandHandler("start", start))

    # Registra el manejador para mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Inicia el bot
    application.run_polling() """

if __name__ == '__main__':
    main()