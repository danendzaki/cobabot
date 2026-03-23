from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime
import calendar
from db_cobabot import conn, cursor, init_db

init_db()

# ================= MENU =================
def menu():
    return ReplyKeyboardMarkup([
        ["➕ Tambah Tugas"],
        ["📋 Lihat Tugas"],
        ["📊 Statistik"]
    ], resize_keyboard=True)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 To-Do Bot PRO MAX", reply_markup=menu())

# ================= TAMBAH =================
async def tambah(update, context):
    context.user_data["state"] = "nama"
    await update.message.reply_text("✏️ Masukkan nama tugas:")

# ================= HANDLE =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    state = context.user_data.get("state")

    if state == "nama":
        context.user_data["nama"] = text
        await pilih_tahun(update)

    elif text == "➕ Tambah Tugas":
        await tambah(update, context)

    elif text == "📋 Lihat Tugas":
        await tampilkan_tugas(update, context)

    elif text == "📊 Statistik":
        await statistik(update, context)

# ================= PILIH TAHUN =================
async def pilih_tahun(update):
    tahun = datetime.now().year

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(str(tahun), callback_data=f"tahun_{tahun}")],
        [InlineKeyboardButton(str(tahun+1), callback_data=f"tahun_{tahun+1}")]
    ])

    await update.message.reply_text("📅 Pilih Tahun:", reply_markup=keyboard)

# ================= PILIH BULAN =================
async def pilih_bulan(query):
    bulan = [
        ("Jan", "01"), ("Feb", "02"), ("Mar", "03"),
        ("Apr", "04"), ("Mei", "05"), ("Jun", "06"),
        ("Jul", "07"), ("Agu", "08"), ("Sep", "09"),
        ("Okt", "10"), ("Nov", "11"), ("Des", "12")
    ]

    keyboard = []
    for i in range(0, 12, 3):
        keyboard.append([
            InlineKeyboardButton(bulan[i][0], callback_data=f"bulan_{bulan[i][1]}"),
            InlineKeyboardButton(bulan[i+1][0], callback_data=f"bulan_{bulan[i+1][1]}"),
            InlineKeyboardButton(bulan[i+2][0], callback_data=f"bulan_{bulan[i+2][1]}")
        ])

    await query.edit_message_text("📆 Pilih Bulan:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= PILIH TANGGAL =================
async def pilih_tanggal(query, context):
    keyboard = []
    row = []

    for i in range(1, 33):
        row.append(InlineKeyboardButton(str(i), callback_data=f"tgl_{i}"))

        if len(row) == 4:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await query.edit_message_text("📅 Pilih Tanggal:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= TAMPILKAN (ANTI CRASH) =================
async def tampilkan_tugas(update_or_query, context):
    user_id = update_or_query.effective_user.id

    cursor.execute("SELECT * FROM tugas WHERE user_id=? ORDER BY deadline ASC", (user_id,))
    data = cursor.fetchall()

    if not data:
        await update_or_query.message.reply_text("📭 Tidak ada tugas", reply_markup=menu())
        return

    teks = "📋 Daftar Tugas:\n\n"
    keyboard = []

    for d in data:
        try:
            deadline = datetime.strptime(d[3], "%Y-%m-%d").date()
            today = datetime.now().date()

            if d[5] == "selesai":
                status = "✅"
            elif deadline < today:
                status = "❗ Terlambat"
            elif deadline == today:
                status = "🔥 Hari ini"
            else:
                status = "⏳"

            deadline_text = d[3]

        except:
            # 💥 DATA RUSAK
            status = "⚠️ ERROR"
            deadline_text = f"{d[3]} (invalid)"

        teks += f"{status} {d[2]}\n📅 {deadline_text} | 🔥 {d[4]}\n\n"

        keyboard.append([
            InlineKeyboardButton("✅", callback_data=f"selesai_{d[0]}"),
            InlineKeyboardButton("❌", callback_data=f"hapus_{d[0]}")
        ])

    if hasattr(update_or_query, "message"):
        await update_or_query.message.reply_text(teks, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update_or_query.edit_message_text(teks, reply_markup=InlineKeyboardMarkup(keyboard))

# ================= BUTTON =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("tahun_"):
        context.user_data["tahun"] = data.split("_")[1]
        await pilih_bulan(query)

    elif data.startswith("bulan_"):
        context.user_data["bulan"] = data.split("_")[1]
        await pilih_tanggal(query, context)

    elif data.startswith("tgl_"):
        tahun = int(context.user_data["tahun"])
        bulan = int(context.user_data["bulan"])
        tanggal = int(data.split("_")[1])

        jumlah_hari = calendar.monthrange(tahun, bulan)[1]

        if tanggal > jumlah_hari:
            await query.answer("❌ Tanggal tidak valid!", show_alert=True)
            await pilih_tanggal(query, context)
            return

        deadline = f"{tahun}-{bulan:02d}-{tanggal:02d}"
        context.user_data["deadline"] = deadline

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 High", callback_data="prio_High")],
            [InlineKeyboardButton("⚡ Medium", callback_data="prio_Medium")],
            [InlineKeyboardButton("💤 Low", callback_data="prio_Low")]
        ])

        await query.edit_message_text(f"📅 Deadline: {deadline}\nPilih prioritas:", reply_markup=keyboard)

    elif data.startswith("prio_"):
        prioritas = data.split("_")[1]
        user_id = update.effective_user.id

        cursor.execute(
            "INSERT INTO tugas (user_id, nama_tugas, deadline, prioritas, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, context.user_data["nama"], context.user_data["deadline"], prioritas, "pending")
        )
        conn.commit()

        context.user_data.clear()

        await query.edit_message_text("✅ Tugas berhasil ditambahkan!")
        await context.bot.send_message(chat_id=user_id, text="Kembali ke menu:", reply_markup=menu())

    elif data.startswith("selesai_"):
        id_tugas = int(data.split("_")[1])
        cursor.execute("UPDATE tugas SET status='selesai' WHERE id=?", (id_tugas,))
        conn.commit()
        await tampilkan_tugas(query, context)

    elif data.startswith("hapus_"):
        id_tugas = int(data.split("_")[1])
        cursor.execute("DELETE FROM tugas WHERE id=?", (id_tugas,))
        conn.commit()
        await tampilkan_tugas(query, context)

# ================= STATISTIK =================
async def statistik(update, context):
    user_id = update.effective_user.id

    cursor.execute("SELECT COUNT(*) FROM tugas WHERE user_id=?", (user_id,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tugas WHERE user_id=? AND status='selesai'", (user_id,))
    selesai = cursor.fetchone()[0]

    pending = total - selesai

    await update.message.reply_text(
        f"📊 Statistik\n\nTotal: {total}\nSelesai: {selesai}\nPending: {pending}",
        reply_markup=menu()
    )

# ================= RUN =================
app = ApplicationBuilder().token("8638351782:AAF5pqJp74rP2fL0FJ0ITjAV6TPHsOBA_ZM").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()