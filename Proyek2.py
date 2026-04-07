from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from db_proyek2 import init_db, tambah_produk, get_produk, kurangi_stok
from service_proyek2 import simpan_pesanan, ambil_pesanan, hapus_pesanan

OWNER_ID = 8660243218

init_db()
tambah_produk()

def menu():
    return ReplyKeyboardMarkup([
        ["📦 Paket", "📊 Stok"]
    ], resize_keyboard=True)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selamat datang!", reply_markup=menu())

# LIHAT PAKET
async def paket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_produk()
    teks = "📦 DAFTAR PAKET:\n\n"
    keyboard = []

    for d in data:
        teks += f"{d[0]} - Rp{d[1]} (Stok: {d[2]})\n"
        keyboard.append([
            InlineKeyboardButton(f"Beli {d[0]}", callback_data=f"beli_{d[0]}")
        ])

    await update.message.reply_text(teks, reply_markup=InlineKeyboardMarkup(keyboard))

# BUTTON
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # ================= BELI =================
    if data.startswith("beli_"):
        nama = data.replace("beli_", "")
        simpan_pesanan(user_id, nama)

        keyboard = [
            [InlineKeyboardButton("💳 Bayar", callback_data="bayar")]
        ]

        await query.edit_message_text(
            f"🛒 Kamu pilih {nama}\nKlik bayar untuk lanjut",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ================= BAYAR =================
    elif data == "bayar":
        keyboard = [
            [InlineKeyboardButton("✅ Konfirmasi", callback_data="konfirmasi")]
        ]

        await query.edit_message_text(
            "💳 Silakan transfer:\n\n"
            "🏦 BCA: 123456789\n"
            "📱 DANA/OVO: 08123456789\n\n"
            "Gunakan m-banking / e-wallet\n\n"
            "Klik konfirmasi setelah bayar",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ================= KONFIRMASI =================
    elif data == "konfirmasi":
        nama = ambil_pesanan(user_id)

        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🛒 KONFIRMASI\nUser: {user_id}\nProduk: {nama}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ACC", callback_data=f"acc_{user_id}")]
            ])
        )

        await query.edit_message_text("⏳ Menunggu admin...")

    # ================= ACC =================
    elif data.startswith("acc_"):
        uid = int(data.split("_")[1])
        nama = ambil_pesanan(uid)

        kurangi_stok(nama)

        await context.bot.send_message(
            uid,
            f"✅ Pesanan {nama} berhasil!\nTerima kasih 🙏"
        )

        hapus_pesanan(uid)

        await query.edit_message_text("✔ Pesanan di-ACC")

# STOK
async def stok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_produk()
    teks = "📊 STOK:\n"
    for d in data:
        teks += f"{d[0]}: {d[2]}\n"
    await update.message.reply_text(teks)

# HANDLE MENU
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📦 Paket":
        await paket(update, context)
    elif text == "📊 Stok":
        await stok(update, context)

# RUN
app = ApplicationBuilder().token("8577954057:AAHC1yLDoRgGNbCXoBHvaVTIeSdPIthwF_w").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()