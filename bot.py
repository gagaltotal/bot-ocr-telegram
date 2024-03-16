import pytesseract
import telebot
import magic
import os
from PIL import Image
from telebot import types
from config_token import *

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    bot.send_message(message.chat.id, "Selamat datang! Saya dapat mengenali teks dari foto Anda. "
                                      "Untuk ini kirimkan foto Anda kepada saya sebagai *File*.", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_welcome_message(message):
    bot.send_message(message.chat.id, "Menu Bantuan Lur ! "
                                      "Anda hanya bisa mengirim format jpg, jpeg, dan png", parse_mode='Markdown')

@bot.message_handler(content_types=['photo'])  # jika pengguna mengirim foto sebagai foto - minta dia mengirimkannya sebagai file
def warning_message(message):
    bot.send_message(message.chat.id, 'Harap kirimkan foto sebagai *File*, bukan sebagai *Photo*', parse_mode='Markdown')


@bot.message_handler(content_types=['document'])
def check_mime_type_of_file(message):  # magic library digunakan untuk memeriksa jenis mime dari file pengiriman
    file = bot.get_file(message.document.file_id)
    download_file = bot.download_file(file.file_path)

    src = message.document.file_id

    with open(src, 'wb') as f:
        f.write(download_file)

    check_format = magic.from_file(src, mime=True)

    if check_format == 'image/jpeg' or check_format == 'image/png':
        os.remove(src)

        with open('user_photo.jpeg', 'wb') as f:
            f.write(download_file)

        buttons(message)
    else:
        bot.send_message(message.chat.id, "Ini bukan foto! Saya hanya bekerja dengan format `jpeg` dan `png`.",
                         parse_mode='Markdown')
        os.remove(src)


def text_detector(message, language):
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text='Proses dimulai.' + '\n' + 'Tolong, tunggu sampai akhir. ')

    img = Image.open('user_photo.jpeg')
    text = pytesseract.image_to_string(img, lang=language)

    if len(text) > 4096:  # konstruk yang digunakan untuk membagi teks besar menjadi dua pesan
        for x in range(0, len(text), 4096):
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text[x:x + 4096])
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text)

    os.remove('user_photo.jpeg')


def buttons(message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='English', callback_data='language_english')
    button2 = types.InlineKeyboardButton(text='Indonesia', callback_data='language_indonesia')
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id, 'Pilih Bahasa photo ke text.', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'language_english':
        text_detector(call.message, 'eng')
    elif call.data == 'language_indonesia':
        text_detector(call.message, 'ind')


if __name__ == '__main__':
    bot.polling(True)
