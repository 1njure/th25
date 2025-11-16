import telebot
import json
from dotenv import load_dotenv
import os
from model import pdf2json
import re

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
    if message.content_type != 'photo' and message.document.mime_type == 'application/pdf':
        print(f'Получен файл для обработки в чате {message.chat.id} (№{message.message_id})')
        bot_message = bot.reply_to(message, f'Файл отправлен в обработку, пожалуйста, подождите...', parse_mode='Markdown')
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем файл на сервере
        file_name = f"temp_{message.message_id}.pdf"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Здесь вызов модели для обработки PDF
        output = pdf2json(file_name)

        # Удаляем временный файл после обработки
        os.remove(file_name)

        # Вывод полученного JSON для отладки
        print(output)

        if "NOT_RECEIPT" in output:
            bot.edit_message_text('Отправленный файл не был определен как чек.', bot_message.chat.id, bot_message.message_id)
            return

        if "ERROR" in output[0]:
            bot.edit_message_text('При обработке файла произошла ошибка', bot_message.chat.id, bot_message.message_id)
            print(f'ОШИБКА: При обработке файла в чате {message.chat.id} (№{message.message_id}) произошла ошибка: {output[1]}')
            return

        # Получение оригинального названия файла
        output_name = f'output_{message.message_id}.json'

        # Сохраняем вывод на сервере
        with open(f'{output_name}', 'w') as new_file:
            new_file.write(output)

        # Отправляем результат пользователю
        try:
            with open(f'{output_name}', 'rb') as f:
                bot.send_document(message.chat.id, f, caption="Запрос обработан успешно", reply_to_message_id=message.message_id, parse_mode='Markdown')
                print(f"Файл в чате {message.chat.id} (№{message.message_id}) обработан успешно")
        except Exception as e:
            bot.edit_message_text('Произошла ошибка отправки результата.', bot_message.chat.id, bot_message.message_id)
            print(f"ОШИБКА: При отправке файла в чате {message.chat.id} (№{message.message_id}) произошла ошибка: {e}")
        else:
            bot.delete_message(bot_message.chat.id, bot_message.message_id)
            os.remove(output_name)

    else:
        bot.reply_to(message, "Пожалуйста, отправьте файл в формате PDF.")

if __name__ == "__main__":
    print('Бот запущен!')
    bot.polling()
    print('Бот завершил работу.')