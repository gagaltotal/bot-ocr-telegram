import pytesseract
import telebot
import magic
import os
import sys
import re
import time
import logging
from PIL import Image, UnidentifiedImageError
from telebot import types
from config_token import *

# ============================================
#           ASCII ART BANNER
# ============================================
BANNER = r"""
██████╗  ██████╗ ████████╗     ██████╗  ██████╗██████╗     ████████╗ ██████╗ ████████╗
██╔══██╗██╔═══██╗╚══██╔══╝    ██╔═══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║   ██║       ██║   ██║██║     ██████╔╝       ██║   ██║   ██║   ██║   
██╔══██╗██║   ██║   ██║       ██║   ██║██║     ██╔══██╗       ██║   ██║   ██║   ██║   
██████╔╝╚██████╔╝   ██║       ╚██████╔╝╚██████╗██║  ██║       ██║   ╚██████╔╝   ██║   
╚═════╝  ╚═════╝    ╚═╝        ╚═════╝  ╚═════╝╚═╝  ╚═╝       ╚═╝    ╚═════╝    ╚═╝   
[ Image to Text Converter ] - Version 1.1
Author: GhostGTR666 - Gagaltotal
Github: github.com/gagaltotal
"""

# ============================================
#           CONFIGURATION & SETUP
# ============================================
# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Direktori untuk file sementara
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Batas ukuran teks Telegram
MAX_TEXT_LENGTH = 4096

# Format gambar yang didukung
SUPPORTED_MIME_TYPES = ['image/jpeg', 'image/png']
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# Dictionary untuk menyimpan path file sementara per user
user_temp_files = {}

# ============================================
#           TOKEN VALIDATION
# ============================================
def validate_bot_token(token) -> tuple[bool, str]:
    """
    Validasi BOT_TOKEN sebelum inisialisasi bot.
    
    Returns:
        tuple[bool, str]: (status_valid, pesan_error)
    """

    if token is None:
        return False, (
            "\n"
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║                       ERROR: TOKEN MISSING                    ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║                                                               ║\n"
            "║  Variabel 'BOT_TOKEN' tidak ditemukan di file config_token.py ║\n"
            "║                                                               ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║     CARA MEMPERBAIKI:                                         ║\n"
            "║                                                               ║\n"
            "║  1. Buka file 'config_token.py'                               ║\n"
            "║  2. Tambahkan baris berikut:                                  ║\n"
            "║                                                               ║\n"
            "║     BOT_TOKEN = \"123456789:ABCdefGHIjklMNOpqrsTUVwxyz\"      ║\n"
            "║                                                               ║\n"
            "║  3. Ganti dengan token bot Anda dari @BotFather               ║\n"
            "║                                                               ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║    Cara mendapatkan token:                                    ║\n"
            "║                                                               ║\n"
            "║  1. Buka Telegram, cari @BotFather                            ║\n"
            "║  2. Kirim /newbot                                             ║\n"
            "║  3. Ikuti instruksi untuk membuat bot baru                    ║\n"
            "║  4. Salin token yang diberikan BotFather                      ║\n"
            "║                                                               ║\n"
            "╚═══════════════════════════════════════════════════════════════╝\n"
        )
    
    if not isinstance(token, str) or not token.strip():
        return False, (
            "\n"
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║                        ERROR: TOKEN EMPTY                     ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║                                                               ║\n"
            "║  Variabel 'BOT_TOKEN' ditemukan tapi nilainya kosong.         ║\n"
            "║                                                               ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║     CARA MEMPERBAIKI:                                         ║\n"
            "║                                                               ║\n"
            "║  Isi token di file 'config_token.py':                         ║\n"
            "║                                                               ║\n"
            "║     BOT_TOKEN = \"123456789:ABCdefGHIjklMNOpqrsTUVwxyz\"      ║\n"
            "║                                                               ║\n"
            "║  Jangan biarkan kosong seperti: BOT_TOKEN = \"\"              ║\n"
            "║                                                               ║\n"
            "╚═══════════════════════════════════════════════════════════════╝\n"
        )
    
    token_pattern = r'^\d{8,10}:[A-Za-z0-9_-]{35}$'
    if not re.match(token_pattern, token.strip()):
        return False, (
            "\n"
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║                     ERROR: INVALID TOKEN FORMAT               ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║                                                               ║\n"
            f"║  Token yang dimasukkan tidak sesuai format Telegram.         ║\n"
            f"║  Token yang diberikan: \"{token[:20]}{'...' if len(token) > 20 else ''}\"       ║\n"
            "║                                                               ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║     FORMAT TOKEN YANG BENAR:                                  ║\n"
            "║                                                               ║\n"
            "║  Contoh: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567         ║\n"
            "║                                                               ║\n"
            "║  Format: [ID_Bot]:[Kunci_API_35_karakter]                    ║\n"
            "║                                                               ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║     TIPS:                                                     ║\n"
            "║                                                               ║\n"
            "║  • Pastikan tidak ada spasi di awal/akhir token               ║\n"
            "║  • Pastikan token disalin lengkap dari @BotFather             ║\n"
            "║  • Jangan menambahkan karakter lain                          ║\n"
            "║                                                               ║\n"
            "╚═══════════════════════════════════════════════════════════════╝\n"
        )
    
    try:
        import requests
        test_url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(test_url, timeout=10)
        result = response.json()
        
        if not result.get('ok'):
            error_code = result.get('error_code', 'Unknown')
            error_desc = result.get('description', 'Unknown error')
            
            if error_code == 401:
                return False, (
                    "\n"
                    "╔═══════════════════════════════════════════════════════════════╗\n"
                    "║                    ERROR: UNAUTHORIZED (401)                  ║\n"
                    "╠═══════════════════════════════════════════════════════════════╣\n"
                    "║                                                               ║\n"
                    "║  Token ditolak oleh server Telegram.                          ║\n"
                    "║  Kemungkinan token sudah tidak valid atau salah.              ║\n"
                    "║                                                               ║\n"
                    "╠═══════════════════════════════════════════════════════════════╣\n"
                    "║     CARA MEMPERBAIKI:                                         ║\n"
                    "║                                                               ║\n"
                    "║  1. Buka @BotFather di Telegram                               ║\n"
                    "║  2. Kirim /mybots                                             ║\n"
                    "║  3. Pilih bot Anda                                            ║\n"
                    "║  4. Pilih 'API Token' untuk melihat token yang benar          ║\n"
                    "║  5. Salin dan ganti token di config_token.py                  ║\n"
                    "║                                                               ║\n"
                    "║  Atau buat token baru:                                        ║\n"
                    "║  1. Kirim /revoke ke @BotFather                               ║\n"
                    "║  2. Pilih bot Anda                                            ║\n"
                    "║  3. Token lama akan diinvalidasi, token baru diberikan        ║\n"
                    "║                                                               ║\n"
                    "╚═══════════════════════════════════════════════════════════════╝\n"
                )
            else:
                return False, (
                    f"\n"
                    f"╔═══════════════════════════════════════════════════════════════╗\n"
                    f"║                 ERROR: API ERROR ({error_code})               ║\n"
                    f"╠═══════════════════════════════════════════════════════════════╣\n"
                    f"║                                                               ║\n"
                    f"║  Deskripsi: {error_desc[:50]:<50}                             ║\n"
                    f"║                                                               ║\n"
                    f"╚═══════════════════════════════════════════════════════════════╝\n"
                )
        
        bot_info = result.get('result', {})
        bot_username = bot_info.get('username', 'Unknown')
        bot_name = bot_info.get('first_name', 'Unknown')
        
        logger.info(f"Token valid! Bot: @{bot_username} ({bot_name})")
        
    except requests.exceptions.Timeout:
        return False, (
            "\n"
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║                     ERROR: CONNECTION TIMEOUT                 ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║                                                               ║\n"
            "║  Tidak dapat terhubung ke server Telegram (timeout).          ║\n"
            "║                                                               ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║     KEMUNGKINAN PENYEBAB:                                     ║\n"
            "║                                                               ║\n"
            "║  • Koneksi internet tidak stabil                              ║\n"
            "║  • Server Telegram sedang bermasalah                          ║\n"
            "║  • Firewall memblokir akses ke api.telegram.org               ║\n"
            "║                                                               ║\n"
            "╚═══════════════════════════════════════════════════════════════╝\n"
        )
    except requests.exceptions.ConnectionError:
        return False, (
            "\n"
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║                     ERROR: NO CONNECTION                      ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            "║                                                               ║\n"
            "║  Tidak dapat terhubung ke server Telegram.                    ║\n"
            "║  Pastikan komputer Anda memiliki koneksi internet.            ║\n"
            "║                                                               ║\n"
            "╚═══════════════════════════════════════════════════════════════╝\n"
        )
    except ImportError:
        logger.warning("Library 'requests' tidak ditemukan, skip API test.")
    except Exception as e:
        logger.warning(f"Gagal test API: {e}")
    
    return True, ""


# ============================================
#           INISIALISASI BOT (DENGAN VALIDASI)
# ============================================
def init_bot():
    """
    Inisialisasi bot dengan validasi token terlebih dahulu.
    
    Returns:
        telebot.TeleBot | None: Instance bot jika valid, None jika gagal
    """
    print(BANNER)
    print("\n Memvalidasi BOT_TOKEN...\n")
    
    is_valid, error_msg = validate_bot_token(BOT_TOKEN)
    
    if not is_valid:
        print(error_msg)
        logger.error("Validasi BOT_TOKEN gagal. Program dihentikan.")
        return None
    
    try:
        bot_instance = telebot.TeleBot(BOT_TOKEN)
        logger.info("Bot berhasil diinisialisasi!")
        return bot_instance
    except Exception as e:
        print(
            "\n"
            "╔═══════════════════════════════════════════════════════════════╗\n"
            "║                     ERROR: INIT FAILED                        ║\n"
            "╠═══════════════════════════════════════════════════════════════╣\n"
            f"║  {str(e)[:55]:<57}                                           ║\n"
            "╚═══════════════════════════════════════════════════════════════╝\n"
        )
        logger.error(f"Gagal inisialisasi bot: {e}")
        return None


bot = init_bot()

if bot is None:
    print("\n Program dihentikan karena error konfigurasi.")
    sys.exit(1)


# ============================================
#           HELPER FUNCTIONS
# ============================================
def get_temp_filepath(user_id: int, original_filename: str) -> str:
    """
    Membuat path file sementara yang unik berdasarkan user_id dan timestamp
    """
    timestamp = int(time.time())
    ext = os.path.splitext(original_filename)[1].lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        ext = '.jpg'
    
    filename = f"{user_id}_{timestamp}{ext}"
    return os.path.join(TEMP_DIR, filename)


def cleanup_temp_file(filepath: str) -> None:
    """
    Menghapus file sementara dengan aman
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"File dihapus: {filepath}")
    except OSError as e:
        logger.error(f"Gagal menghapus file {filepath}: {e}")


def split_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> list:
    """
    Memecah teks panjang menjadi beberapa bagian
    """
    if not text or len(text) <= max_length:
        return [text] if text else []
    
    chunks = []
    for i in range(0, len(text), max_length):
        chunks.append(text[i:i + max_length])
    
    return chunks


def escape_markdown(text: str) -> str:
    """
    Escape karakter khusus Markdown untuk menghindari error parsing
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


# ============================================
#           BOT HANDLERS
# ============================================
@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    """Handler untuk command /start"""
    welcome_text = (
        f"```\n{BANNER}\n```\n\n"
        "Selamat datang! \n\n"
        "Saya dapat mengenali teks dari foto Anda.\n"
        "Untuk menggunakan, kirimkan foto Anda sebagai *File* "
        "(bukan sebagai Photo).\n\n"
        "*Format didukung:* `jpg`, `jpeg`, `png`"
    )
    
    try:
        bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error di /start: {e}")
        bot.send_message(
            message.chat.id,
            "Selamat datang! Saya dapat mengenali teks dari foto. Kirim foto sebagai File."
        )


@bot.message_handler(commands=['help'])
def send_help_message(message):
    """Handler untuk command /help"""
    help_text = (
        "*Menu Bantuan*\n\n"
        "*Cara Penggunaan:*\n"
        "1. Kirim foto sebagai *File* (bukan Photo)\n"
        "2. Pilih bahasa yang diinginkan\n"
        "3. Tunggu proses selesai\n\n"
        "*Format yang didukung:*\n"
        "• `jpg` / `jpeg`\n"
        "• `png`\n\n"
        "*Catatan:*\n"
        "• Foto harus jelas dan tidak blur\n"
        "• Teks harus terbaca dengan baik\n"
        "• Ukuran file maksimal 20MB"
    )
    
    try:
        bot.send_message(
            message.chat.id,
            help_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error di /help: {e}")
        bot.send_message(
            message.chat.id,
            "Kirim foto sebagai File (bukan Photo). Format: jpg, jpeg, png"
        )


@bot.message_handler(content_types=['photo'])
def warning_photo_message(message):
    """Handler jika pengguna mengirim foto sebagai Photo (bukan File)"""
    warning_text = (
        "*Perhatian!*\n\n"
        "Harap kirimkan foto sebagai *File*, bukan sebagai *Photo*.\n\n"
        "*Cara mengirim sebagai File:*\n"
        "1. Tap ikon klip 📎\n"
        "2. Pilih *File*\n"
        "3. Pilih foto dari galeri"
    )
    
    try:
        bot.send_message(
            message.chat.id,
            warning_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error di photo handler: {e}")
        bot.send_message(
            message.chat.id,
            "Harap kirimkan foto sebagai File, bukan sebagai Photo."
        )


@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Handler untuk menerima file document"""
    user_id = message.from_user.id
    
    if not message.document.file_name:
        bot.send_message(
            message.chat.id,
            "File tidak memiliki nama. Harap kirim file yang valid."
        )
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        temp_filepath = get_temp_filepath(user_id, message.document.file_name)
        
        with open(temp_filepath, 'wb') as f:
            f.write(downloaded_file)
        
        logger.info(f"File didownload: {temp_filepath}")
        
        detected_mime = magic.from_file(temp_filepath, mime=True)
        logger.info(f"MIME type terdeteksi: {detected_mime}")
        
        if detected_mime not in SUPPORTED_MIME_TYPES:
            bot.send_message(
                message.chat.id,
                f"Format file tidak didukung!\n\n"
                f"Format terdeteksi: `{detected_mime}`\n"
                f"Format yang didukung: `jpeg`, `png`",
                parse_mode='Markdown'
            )
            cleanup_temp_file(temp_filepath)
            return
        
        try:
            with Image.open(temp_filepath) as img:
                img.verify()
        except UnidentifiedImageError:
            bot.send_message(
                message.chat.id,
                "File bukan gambar yang valid atau file rusak."
            )
            cleanup_temp_file(temp_filepath)
            return
        except Exception as img_error:
            logger.error(f"Error verifikasi gambar: {img_error}")
            bot.send_message(
                message.chat.id,
                "Gagal memverifikasi gambar. File mungkin rusak."
            )
            cleanup_temp_file(temp_filepath)
            return
        
        user_temp_files[user_id] = temp_filepath
        
        send_language_buttons(message)
        
    except Exception as e:
        logger.error(f"Error di handle_document: {e}")
        bot.send_message(
            message.chat.id,
            "Terjadi kesalahan saat memproses file. Silakan coba lagi."
        )
        if user_id in user_temp_files:
            cleanup_temp_file(user_temp_files[user_id])
            del user_temp_files[user_id]


def send_language_buttons(message):
    """Mengirim tombol pilihan bahasa"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    button_eng = types.InlineKeyboardButton(
        text='English',
        callback_data='language_english'
    )
    button_ind = types.InlineKeyboardButton(
        text='Indonesia',
        callback_data='language_indonesia'
    )
    
    keyboard.add(button_eng, button_ind)
    
    try:
        bot.send_message(
            message.chat.id,
            "*Pilih Bahasa untuk OCR*\n\n"
            "Pilih bahasa teks yang ada di foto:",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error mengirim tombol: {e}")
        bot.send_message(
            message.chat.id,
            "Pilih bahasa:",
            reply_markup=keyboard
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('language_'))
def handle_language_selection(call):
    """Handler untuk callback query pemilihan bahasa"""
    user_id = call.from_user.id
    
    temp_filepath = user_temp_files.get(user_id)
    
    if not temp_filepath or not os.path.exists(temp_filepath):
        bot.answer_callback_query(
            call.id,
            "File tidak ditemukan. Silakan kirim ulang foto.",
            show_alert=True
        )
        if user_id in user_temp_files:
            del user_temp_files[user_id]
        return
    
    language_map = {
        'language_english': ('eng', 'English'),
        'language_indonesia': ('ind', 'Indonesia')
    }
    
    lang_code, lang_name = language_map.get(call.data, ('eng', 'English'))
    
    bot.answer_callback_query(
        call.id,
        f"Memproses dengan bahasa {lang_name}...",
        show_alert=False
    )
    
    process_ocr(call.message, temp_filepath, lang_code, user_id)


def process_ocr(message, filepath: str, language: str, user_id: int):
    """
    Fungsi utama untuk memproses OCR pada gambar
    """
    processing_msg = None
    
    try:
        processing_msg = bot.send_message(
            message.chat.id,
            "*Memproses gambar...*\n\n"
            "Mohon tunggu, ini mungkin memakan waktu beberapa detik.",
            parse_mode='Markdown'
        )
        
        with Image.open(filepath) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            text = pytesseract.image_to_string(img, lang=language)

        text = text.strip()
        
        if not text:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text="*Hasil Kosong*\n\n"
                     "Tidak dapat mendeteksi teks dalam gambar.\n"
                     "Pastikan gambar memiliki teks yang jelas.",
                parse_mode='Markdown'
            )
            return
        
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        
        text_chunks = split_text(text)

        if text_chunks:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text=f"*Hasil OCR:*\n\n```\n{text_chunks[0]}\n```",
                parse_mode='Markdown'
            )
            
            for chunk in text_chunks[1:]:
                bot.send_message(
                    message.chat.id,
                    f"```\n{chunk}\n```",
                    parse_mode='Markdown'
                )
        
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract tidak ditemukan")
        if processing_msg:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text="*Error: Tesseract tidak terinstal*\n\n"
                     "Silakan hubungi administrator.",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Error saat OCR: {e}")
        error_msg = "Terjadi kesalahan saat memproses gambar."
        
        if "language" in str(e).lower():
            error_msg = f"Bahasa '{language}' tidak tersedia.\nPastikan paket bahasa Tesseract sudah terinstal."
        
        if processing_msg:
            try:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=processing_msg.message_id,
                    text=error_msg,
                    parse_mode='Markdown'
                )
            except Exception:
                bot.send_message(message.chat.id, error_msg)
    
    finally:
        cleanup_temp_file(filepath)
        
        if user_id in user_temp_files:
            del user_temp_files[user_id]


# ============================================
#           ERROR HANDLERS
# ============================================
@bot.message_handler(func=lambda message: True)
def handle_unknown_messages(message):
    """Handler untuk pesan yang tidak dikenali"""
    bot.send_message(
        message.chat.id,
        "Saya tidak mengerti pesan Anda.\n\n"
        "Kirim foto sebagai *File* untuk memulai OCR,\n"
        "atau ketik /help untuk bantuan.",
        parse_mode='Markdown'
    )


# ============================================
#           MAIN EXECUTION
# ============================================
if __name__ == '__main__':
    print("\n BOT_TOKEN tervalidasi!")
    print("   Bot OCR sedang berjalan...")
    print("   Tekan Ctrl+C untuk menghentikan.\n")
    
    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60,
            allowed_updates=['message', 'callback_query']
        )
    except KeyboardInterrupt:
        print("\n\n Bot dihentikan oleh pengguna.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        print(f"\n Fatal error: {e}")
    finally:
        print("\n Membersihkan file sementara...")
        for filepath in list(user_temp_files.values()):
            cleanup_temp_file(filepath)
        user_temp_files.clear()
        print("Cleanup selesai.")