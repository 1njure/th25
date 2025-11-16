import telebot
import json
from dotenv import load_dotenv
import os
from model import pdf2json

load_dotenv()

# Получаем токен бота из переменной среды
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Не задана переменная среды TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# Обработчик команд /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне PDF-файл, и я преобразую его содержимое в JSON.")

@bot.message_handler(content_types=['document', 'photo'])
def handle_document(message):
    # Проверяем, что загруженный файл - PDF
    if message.document.mime_type == 'application/pdf':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем файл на сервере (или обрабатываем в памяти)
        file_name = f"temp_{message.message_id}.pdf"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Здесь вызов модели для обработки PDF
        output = pdf2json(file_name)

        # Удаляем временный файл после обработки
        os.remove(file_name)

        # Вывод полученного JSON для отладки
        print(output)

        # Отправляем результат пользователю
        bot.reply_to(message, f'{output}', parse_mode='Markdown')

    else:
        bot.reply_to(message, "Пожалуйста, отправьте файл в формате PDF.")

if __name__ == "__main__":
    print('Бот запущен!')
    bot.polling()
    print('Бот завершил работу.')