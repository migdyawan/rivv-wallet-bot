import telebot
from telebot import types
import os
from datetime import datetime
import re

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

saldo = 0
history = []

def format_rupiah(angka):
    return f"{angka:,}".replace(",", ".")

def parse_nominal(text):
    text = text.lower().replace(".", "").replace(",", "")
    
    angka = re.search(r'(\d+)', text)
    if not angka:
        return 0
    
    nilai = int(angka.group(1))

    if "jt" in text:
        nilai *= 1000000
    elif "rb" in text:
        nilai *= 1000

    return nilai

def detect_dompet(text):
    text = text.lower()
    if "cash" in text:
        return "Cash"
    if "mandiri" in text:
        return "Mandiri"
    if "bri" in text:
        return "BRI"
    if "bca" in text:
        return "BCA"
    if "qris" in text:
        return "QRIS"
    return "Cash"

def detect_kategori(text):
    text = text.lower()
    if any(word in text for word in ["nasi", "makan", "kopi", "minum"]):
        return "Makanan & Minuman"
    if any(word in text for word in ["bensin", "parkir", "transport"]):
        return "Transportasi"
    return "Lainnya"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Status Sisa Uang")
    markup.add("📜 History")
    bot.send_message(message.chat.id, "Rivv Wallet Aktif 💰", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global saldo
    text = message.text.lower()

    if text == "reset":
        saldo = 0
        history.clear()
        bot.send_message(
            message.chat.id,
            "♻️ Saldo dan riwayat berhasil direset."
        )
        return
    
    if text == "📊 status sisa uang":
        bot.send_message(message.chat.id,
                         f"💰 Sisa dana kamu\nRp {format_rupiah(saldo)}")
        return

    if text == "📜 history":
        if not history:
            bot.send_message(message.chat.id, "Belum ada transaksi.")
            return
        bot.send_message(message.chat.id,
                         "📜 Riwayat Transaksi\n\n" + "\n".join(history))
        return
        
    

    if text == "saldo" or text == "/saldo":
        bot.send_message(message.chat.id,
                     f"💳 Sisa dana kamu\nRp {format_rupiah(saldo)}")
    return

if text.startswith("-"):
    nominal = parse_nominal(text)
    saldo -= nominal
    history.append(f"➖ {format_rupiah(nominal)} | Penyesuaian")
    bot.send_message(message.chat.id,
                     f"💳 Saldo dikurangi IDR {format_rupiah(nominal)}\n"
                     f"Sisa dana: IDR {format_rupiah(saldo)}")
    return


    nominal = parse_nominal(text)
    if nominal == 0:
        return

    dompet = detect_dompet(text)
    tanggal = datetime.now().strftime("%d-%m-%Y")

    if any(word in text for word in ["gaji", "masuk", "income", "bonus"]):
        saldo += nominal
        history.append(f"➕ {format_rupiah(nominal)} | Pemasukan")
        bot.send_message(message.chat.id,
                         f"💳 Dana tersimpan IDR {format_rupiah(saldo)}")
    else:
        saldo -= nominal
        kategori = detect_kategori(text)
        keterangan = re.sub(r'\d+.*', '', text).strip().title()

        history.append(f"➖ {format_rupiah(nominal)} | {keterangan}")

        bot.send_message(message.chat.id,
f"""✅ Transaksi Tercatat!
📝 {keterangan}
💵 Rp {format_rupiah(nominal)}
📂 Kategori: {kategori}
📦 Dompet: {dompet}
💳 Sisa dana : {format_rupiah(saldo)}
📅 {tanggal}""")

bot.infinity_polling()
