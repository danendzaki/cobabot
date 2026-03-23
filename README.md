# Telegram Bot Collection

Repository ini berisi beberapa bot Telegram berbasis Python yang dibuat untuk kebutuhan pembelajaran dan implementasi sederhana, seperti manajemen tugas dan simulasi sistem UMKM.

## ✨ Daftar Bot

### 1. To-Do Bot
Bot untuk mengelola tugas harian.

Fitur:
- Tambah tugas (step-by-step)
- Pilih deadline via tombol
- Validasi tanggal (termasuk Februari & tahun kabisat)
- Pilih prioritas (High, Medium, Low)
- Lihat daftar tugas
- Tandai selesai / hapus tugas
- Statistik tugas
- Anti error (data tetap aman meskipun invalid)

---

### 2. UMKM Bot
Bot simulasi sistem penjualan paket produk.

Fitur:
- Lihat daftar paket
- Pilih paket dengan tombol
- Sistem pemesanan
- Konfirmasi pembelian
- Notifikasi ke admin (penjual)
- Sistem approval (admin ACC pesanan)
- Simulasi pembayaran (transfer & e-money)

---

## 🧱 Struktur Project

├── cobabot.py # To-Do Bot (main)
├── db_cobabot.py # Database To-Do Bot
├── umkm_bot.py # UMKM Bot (main)
├── db_umkm.py # Database UMKM Bot
├── todo.db # Database To-Do
└── umkm.db # Database UMKM
