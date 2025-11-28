from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import requests
import datetime

load_dotenv()  # Carrega as keys do .env

TOKEN = os.getenv("TOKEN_TELEGRAM")
API_KEY = os.getenv("OPENWEATHER_KEY")

usuarios = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id not in usuarios:
        usuarios[user_id] = True
        await update.message.reply_text(
            "🌤️ Olá! Eu sou o BotClima!\n"
            "Me diga o nome de uma cidade e eu te informo o clima agora!"
        )
    else:
        await update.message.reply_text("😄 Me diga a cidade novamente:")

async def pegar_clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cidade = update.message.text.strip()

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&units=metric&lang=pt_br"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            await update.message.reply_text("⚠️ Cidade não encontrada. Tente novamente!")
            return

        temp = response["main"]["temp"]
        sensacao = response["main"]["feels_like"]
        temp_min = response["main"]["temp_min"]
        temp_max = response["main"]["temp_max"]
        umidade = response["main"]["humidity"]
        vento = response["wind"]["speed"]
        condicao = response["weather"][0]["description"]

        nascer = datetime.datetime.fromtimestamp(response["sys"]["sunrise"])
        por = datetime.datetime.fromtimestamp(response["sys"]["sunset"])

        msg = (
            f"🌍 *Clima de:* _{cidade}_\n\n"
            f"🌡️ Temperatura: *{temp}°C*\n"
            f"🤗 Sensação térmica: *{sensacao}°C*\n"
            f"🔽 Mínima: *{temp_min}°C* | 🔼 Máxima: *{temp_max}°C*\n\n"
            f"🌥️ Condição: *{condicao}*\n"
            f"💧 Umidade: *{umidade}%*\n"
            f"💨 Vento: *{vento} m/s*\n\n"
            f"🌅 Nascer do sol: *{nascer.strftime('%H:%M')}*\n"
            f"🌇 Pôr do sol: *{por.strftime('%H:%M')}*\n"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ Erro ao buscar clima.")
        print(e)
        

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pegar_clima))

app.run_polling()
