# Bot telegram OCR

Bot Telegram. Mengubah foto Anda menjadi teks.

Program kecil tapi sangat berguna - asisten. Memungkinkan Anda menyalin teks dari tangkapan layar atau gambar Anda.

Cara Installasi di server anda :

- siapkan python 3 dan package nya yaitu pip

jika os server anda turunan debian, ubuntu contoh seperti ini :

- sudo apt install tesseract-ocr -y

kalau berbeda distro dan turunan nya silakan sesuaikan masing-masing package manager nya
contoh di os centos, fedora

- sudo yum install tesseract-ocr | sudo dnf install tesseract-ocr

contoh turunan arch

- sudo pacman -Sy tesseract-ocr

selanjut nya install package bahasa, disini saya menginstall package bahasa english dan indonesia

- sudo apt install tesseract-ocr-eng | sudo apt install tesseract-ocr-ind

install package dari pip yang dibutuhkan untuk ocr ke bot telegram :

- pip install -r requirement.txt

config bot token di file config_token

jalankan bot menggunakan python 3 :

- python3 bot.py