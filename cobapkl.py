from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from db_proyek2 import conn, cursor, init_db, seed_produk

# 👉 GANTI INI DENGAN ID TELEGRAM KAMU
ADMIN_ID = 8660243218

init_db()
seed_produk()

# ================= MENU =================
def menu():
    return ReplyKeyboardMarkup([
        ["📋 Lihat Produk"],
        ["📦 Riwayat"],
        ["💳 Pembayaran"]
    ], resize_keyboard=True)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Selamat datang di UMKM Bot",
        reply_markup=menu()
    )

# ================= PRODUK =================
async def lihat_produk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT * FROM produk")
    data = cursor.fetchall()

    teks = "📦 Daftar Produk:\n\n"
    keyboard = []

    for d in data:
        teks += f"{d[1]}\nIsi: {d[2]}\nHarga: Rp{d[3]}\nStok: {d[4]}\n\n"
        keyboard.append([
            InlineKeyboardButton(f"Beli {d[1]}", callback_data=f"beli_{d[0]}")
        ])

    await update.message.reply_text(teks, reply_markup=InlineKeyboardMarkup(keyboard))

# ================= RIWAYAT =================
async def riwayat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("SELECT nama_produk, status FROM transaksi WHERE user_id=?", (user_id,))
    data = cursor.fetchall()

    if not data:
        await update.message.reply_text("📭 Belum ada pesanan")
        return

    teks = "📦 Riwayat Pesanan:\n\n"

    for d in data:
        status = "⏳ Pending" if d[1] == "pending" else "✅ Selesai"
        teks += f"{d[0]} - {status}\n"

    await update.message.reply_text(teks)

# ================= PEMBAYARAN =================
async def pembayaran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = """
💳 Metode Pembayaran

🏦 Transfer Bank:
BCA - 1234567890

📱 E-Money:
OVO / DANA / GoPay - 08123456789
"""
    await update.message.reply_text(teks)

# ================= BUTTON =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ================= BELI =================
    if data.startswith("beli_"):
        id_produk = int(data.split("_")[1])

        cursor.execute("SELECT * FROM produk WHERE id=?", (id_produk,))
        produk = cursor.fetchone()

        if produk[4] <= 0:
            await query.answer("❌ Stok habis!", show_alert=True)
            return

        user_id = query.from_user.id

        cursor.execute(
            "INSERT INTO transaksi (user_id, nama_produk, status) VALUES (?, ?, ?)",
            (user_id, produk[1], "pending")
        )

        # kurangi stok
        cursor.execute(
            "UPDATE produk SET stok = stok - 1 WHERE id=?",
            (id_produk,)
        )

        conn.commit()

        # kirim ke admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
🛒 ORDER MASUK

👤 User: {user_id}
📦 Produk: {produk[1]}
💰 Harga: Rp{produk[3]}
""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ACC", callback_data=f"acc_{user_id}_{produk[1]}")]
            ])
        )

        await query.edit_message_text("✅ Pesanan dikirim, tunggu admin.")

    # ================= ACC =================
    elif data.startswith("acc_"):
        _, user_id, produk = data.split("_")

        cursor.execute(
            "UPDATE transaksi SET status='selesai' WHERE user_id=? AND nama_produk=? AND status='pending'",
            (user_id, produk)
        )
        conn.commit()

        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"✅ Pesanan {produk} sudah dikonfirmasi.\nTerima kasih!"
        )

        await query.edit_message_text("Pesanan berhasil di-ACC")

# ================= HANDLE =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📋 Lihat Produk":
        await lihat_produk(update, context)

    elif text == "📦 Riwayat":
        await riwayat(update, context)

    elif text == "💳 Pembayaran":
        await pembayaran(update, context)

# ================= RUN =================
app = ApplicationBuilder().token("8718916554:AAErLk3QdxrgymuZHCE_qPKljFxr-KC3Lt8").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()