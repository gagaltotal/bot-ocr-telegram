# Bot OCR Telegram

![Screen Capture](https://raw.githubusercontent.com/gagaltotal/bot-ocr-telegram/refs/heads/main/Screenshot%20from%202026-04-27%2014-44-12.png)

**Bot Telegram untuk Konversi Foto ke Teks**

Bot Telegram canggih yang menggunakan Optical Character Recognition (OCR) untuk mengubah foto/tangkapan layar Anda menjadi teks yang dapat disalin. Mendukung dua bahasa: **English** dan **Indonesia**.

## Daftar Isi
- [Fitur Utama](#fitur-utama)
- [Prasyarat Sistem](#prasyarat-sistem)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Struktur Fungsi](#struktur-fungsi)
- [Troubleshooting](#troubleshooting)

## Fitur Utama

- OCR dengan dukungan bahasa **Inggris** dan **Indonesia**
- Validasi token bot otomatis dengan pesan error yang detail
- Antarmuka tombol untuk pemilihan bahasa
- Pembacaan file dokumen image (JPEG, PNG)
- Deteksi MIME type file otomatis
- Pembagian teks panjang otomatis (chunking)
- Pembersihan file sementara otomatis
- Logging sistem yang terstruktur
- Penanganan error yang komprehensif
- Banner ASCII keren saat startup

## Prasyarat Sistem

### Python dan Dependencies
- Python 3.7+
- pip (Python Package Manager)

### System Dependencies (sesuai distro)

#### Debian/Ubuntu
```bash
sudo apt install tesseract-ocr -y
sudo apt install tesseract-ocr-eng tesseract-ocr-ind -y
```

#### CentOS/Fedora
```bash
sudo yum install tesseract-ocr -y
# atau
sudo dnf install tesseract-ocr -y
```

#### Arch Linux
```bash
sudo pacman -Sy tesseract-ocr -y
```

## Instalasi

### 1. Clone atau Download Repository
```bash
git clone https://github.com/gagaltotal/bot-ocr-telegram.git
cd bot-ocr-telegram
```

### 2. Install System Dependencies
Pilih sesuai distro Linux Anda (lihat bagian [Prasyarat Sistem](#prasyarat-sistem))

# 3. Create virtual environment
```bash
python3 -m venv .venv
```

# On Linux:
```bash
source .venv/bin/activate
```

# On Windows:
```bash
source .venv\Scripts\activate
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Konfigurasi

### Dapatkan Bot Token dari BotFather
1. Buka Telegram dan cari **@BotFather**
2. Kirim perintah `/newbot`
3. Ikuti instruksi untuk membuat bot baru
4. Salin token yang diberikan BotFather

### Konfigurasi Token (config_token.py)
Edit file `config_token.py` dan masukkan token bot Anda:

```python
BOT_TOKEN = 'PASTE_YOUR_TOKEN_HERE'
```

Contoh format token yang benar:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567
```

## Cara Penggunaan

![Screen Capture](https://raw.githubusercontent.com/gagaltotal/bot-ocr-telegram/refs/heads/main/Screenshot%20from%202026-04-27%2015-14-10.png)

### Jalankan Bot
```bash
python bot.py
```

atau

```bash
python3 bot.py
```

### Menggunakan Bot di Telegram
1. Temukan bot Anda di Telegram
2. Kirim perintah `/start` untuk melihat pesan sambutan
3. Kirim perintah `/help` untuk melihat bantuan
4. **Penting:** Kirim foto sebagai **File** (bukan sebagai Photo)
   - Tap ikon klip 📎
   - Pilih "File"
   - Pilih foto dari galeri
5. Pilih bahasa teks: **English** atau **Indonesia**
6. Tunggu hasil OCR dikirim kembali

## Struktur Fungsi

### File: `config_token.py`
- **`BOT_TOKEN`** - Variabel untuk menyimpan token bot Telegram

### File: `bot.py`

#### Fungsi Validasi & Inisialisasi
- **`validate_bot_token(token)`** - Validasi token bot dengan format dan API check
- **`init_bot()`** - Inisialisasi bot dengan tampilan banner

#### Fungsi Helper
- **`get_temp_filepath(user_id, original_filename)`** - Generate path file sementara unik
- **`cleanup_temp_file(filepath)`** - Hapus file sementara dengan aman
- **`split_text(text, max_length)`** - Pecah teks panjang menjadi chunks (max 4096 char)
- **`escape_markdown(text)`** - Escape karakter khusus Markdown

#### Bot Handlers (Command)
- **`send_welcome_message(message)`** - Handler `/start`
- **`send_help_message(message)`** - Handler `/help`

#### Bot Handlers (Document)
- **`handle_document(message)`** - Terima dan validasi file image
- **`warning_photo_message(message)`** - Peringatan jika user kirim Photo

#### Fungsi Interaksi
- **`send_language_buttons(message)`** - Kirim tombol pilihan bahasa
- **`handle_language_selection(call)`** - Handle callback pemilihan bahasa

#### Fungsi OCR Utama
- **`process_ocr(message, filepath, language, user_id)`** - Proses OCR dengan pytesseract

#### Error Handlers
- **`handle_unknown_messages(message)`** - Handle pesan yang tidak dikenali
- **`handle_polling_error(exception)`** - Handle error polling bot

#### Main Loop
- **`bot.infinity_polling()`** - Polling pesan Telegram secara berkelanjutan

## Diagram Alur Fungsi

```
User Sends Photo
       ↓
handle_document() → Validate MIME Type
       ↓
send_language_buttons() → Show Language Options
       ↓
handle_language_selection() → User Pick Language
       ↓
process_ocr() → Run Tesseract OCR
       ↓
split_text() → Split if > 4096 chars
       ↓
Bot Send Result to User
       ↓
cleanup_temp_file() → Delete Temp File
```

## Troubleshooting

### Error: TOKEN MISSING atau TOKEN EMPTY
- Pastikan file `config_token.py` ada
- Pastikan `BOT_TOKEN` diisi dengan token yang benar dari @BotFather

### Error: INVALID TOKEN FORMAT
- Token harus format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567`
- Jangan ada spasi di awal/akhir
- Salin lengkap dari @BotFather

### Error: Tesseract tidak ditemukan
- Pastikan sudah install tesseract-ocr di sistem
- Cek instalasi: `tesseract --version`

### Error: Bahasa tidak tersedia
- Install language pack Tesseract yang diperlukan
- Contoh untuk bahasa Indonesia: `sudo apt install tesseract-ocr-ind`

### Bot tidak merespon
- Cek koneksi internet
- Cek apakah bot sudah di-follow
- Restart bot dengan Ctrl+C kemudian jalankan lagi

## Format File yang Didukung
- `jpg` / `jpeg`
- `png`

**Catatan Penting:** Foto harus jelas dan tidak blur. Teks harus terbaca dengan baik.

## Screenshot
![Screen Capture](https://raw.githubusercontent.com/gagaltotal/bot-ocr-telegram/main/ss.png)

## Author
- **Gagaltotal** (GhostGTR666)
- Github: [github.com/gagaltotal](https://github.com/gagaltotal)

## License
MIT License - Feel free to use this project

## Kontribusi
Kontribusi sangat diterima! Silakan fork, buat branch baru, dan submit pull request.
