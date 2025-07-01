import requests
from bs4 import BeautifulSoup
import openai
import time
import os

# Variables de entorno (Render.com)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

PAIRS = [
    "AUD/CAD", "AUD/JPY", "AUD/NZD", "AUD/USD",
    "CHF/JPY", "EUR/JPY", "EUR/MXN", "EUR/NZD",
    "EUR/USD", "EUR/GBP", "NZD/JPY", "NZD/USD",
    "USD/CHF", "GBP/CHF", "GBP/JPY", "GBP/NZD", "GBP/CAD"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    r = requests.post(url, data=payload)
    return r.status_code

def analyze_sentiment_openai(text):
    prompt = (
        f"Analiza el sentimiento (positivo, negativo o neutral) del siguiente texto financiero:

"
        f""{text}"

"
        f"Responde solo con: POSITIVE, NEGATIVE o NEUTRAL."
    )
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=5,
            temperature=0
        )
        sentiment = response.choices[0].text.strip().upper()
        if sentiment == "POSITIVE":
            return "🟢 Alcista"
        elif sentiment == "NEGATIVE":
            return "🔴 Bajista"
        else:
            return "🟡 Neutro"
    except Exception as e:
        return f"⚠️ Error IA: {e}"

def fetch_forex_news():
    url = "https://www.forexfactory.com/calendar"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    news_items = []
    rows = soup.find_all("tr", {"class": "calendar__row"})

    for row in rows:
        impact = row.find("td", class_="impact")
        if impact and 'high' in impact.get("class", []):
            currency = row.find("td", class_="currency").text.strip()
            title = row.find("td", class_="event").text.strip()
            time_event = row.find("td", class_="time").text.strip()

            for pair in PAIRS:
                if currency in pair:
                    sentiment = analyze_sentiment_openai(title)
                    message = (
                        f"🔔 *Noticia Económica* (ALTO IMPACTO)
"
                        f"🕐 Hora: {time_event}
"
                        f"💱 Moneda: {currency}
"
                        f"📰 Evento: {title}
"
                        f"📊 Par afectado: {pair}

"
                        f"🤖 IA Sentimiento: {sentiment}"
                    )
                    news_items.append(message)
                    break
    return news_items

# Mensaje de arranque
send_telegram_message("🚀 Bot Forex IA iniciado correctamente.")

# Bucle principal
while True:
    noticias = fetch_forex_news()
    if noticias:
        for noticia in noticias:
            send_telegram_message(noticia)
    time.sleep(600)  # Esperar 10 minutos
