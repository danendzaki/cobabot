from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
from db_ujicoba1 import conn, cursor, init_db

init_db()

ADMIN_ID = 8660243218  

def menu_user():
    keyboard = [
        ["📦 Lihat Paket"],
        ["🛒 Beli Paket"],
        ["💰 Konfirmasi"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛍 Selamat datang di UMKM Bot!", reply_markup=menu_user())

async def lihat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT * FROM paket")
    data = cursor.fetchall()

    teks = "📦 Daftar Paket:\n\n"
    for d in data:
        teks += f"{d[0]}. {d[1]}\nHarga: Rp{d[3]}\nStok: {d[4]}\n\n"

    await update.message.reply_text(teks)

async def pilih_beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Paket 1", callback_data="beli_1")],
        [InlineKeyboardButton("Paket 2", callback_data="beli_2")],
        [InlineKeyboardButton("Paket 3", callback_data="beli_3")]
    ])

    await update.message.reply_text("Pilih paket:", reply_markup=keyboard)

async def proses_beli(update: Update, context: ContextTypes.DEFAULT_TYPE, id_paket):
    query = update.callback_query

    cursor.execute("SELECT nama_paket, harga, stok FROM paket WHERE id=?", (id_paket,))
    paket = cursor.fetchone()

    if not paket:
        await query.message.reply_text("❌ Paket tidak ditemukan")
        return

    nama, harga, stok = paket

    if stok <= 0:
        await query.message.reply_text("❌ Stok habis")
        return

    cursor.execute("UPDATE paket SET stok = stok - 1 WHERE id=?", (id_paket,))

    user_id = update.effective_user.id
    user = update.effective_user.username or "User"

    cursor.execute(
        "INSERT INTO transaksi (user_id, user, nama_paket, harga, status) VALUES (?, ?, ?, ?, ?)",
        (user_id, user, nama, harga, "pending")
    )

    transaksi_id = cursor.lastrowid
    conn.commit()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ACC", callback_data=f"acc_{transaksi_id}")]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📢 Pesanan baru!\nUser: @{user}\nPaket: {nama}\nHarga: Rp{harga}",
        reply_markup=keyboard
    )

    await query.message.reply_text(
        f"🛍 Pesanan berhasil!\n{nama}\nRp{harga}\n\n"
        f"💳 Transfer:\nBRI 1234567890\nDana/OVO/GoPay 08123456789\n\n"
        f"Klik 'Konfirmasi' setelah bayar"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("beli_"):
        id_paket = int(query.data.split("_")[1])
        await proses_beli(update, context, id_paket)

    elif query.data.startswith("acc_"):
        if update.effective_user.id != ADMIN_ID:
            await query.answer("❌ Bukan admin!", show_alert=True)
            return

        transaksi_id = int(query.data.split("_")[1])

        cursor.execute("SELECT user_id, nama_paket FROM transaksi WHERE id=?", (transaksi_id,))
        data = cursor.fetchone()

        if not data:
            return

        user_id, nama_paket = data

        cursor.execute("UPDATE transaksi SET status='selesai' WHERE id=?", (transaksi_id,))
        conn.commit()

        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Pesanan kamu ({nama_paket}) sudah diproses!\n🙏 Terima kasih telah berbelanja!"
        )

        await query.edit_message_text("✅ Pesanan di-ACC")

async def konfirmasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username or "User"

    cursor.execute(
        "UPDATE transaksi SET status='dikonfirmasi' WHERE user=? AND status='pending'",
        (user,)
    )
    conn.commit()

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💰 @{user} sudah konfirmasi pembayaran!"
    )

    await update.message.reply_text("✅ Konfirmasi dikirim, tunggu admin")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📦 Lihat Paket":
        await lihat(update, context)

    elif text == "🛒 Beli Paket":
        await pilih_beli(update, context)

    elif text == "💰 Konfirmasi":
        await konfirmasi(update, context)

app = ApplicationBuilder().token("7990338315:AAFz20aJYlUxVyqX4jNVgAEXwWLJ9d2SyjU").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()