import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен напрямую из переменных окружения Railway
TOKEN = os.getenv('BOT_TOKEN')
print(f' Токен загружен: {TOKEN[:10] if TOKEN else "НЕ НАЙДЕН"}...')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f' Получена команда /start от пользователя {update.effective_user.id}')
    try:
        welcome_message = """ <b>IT English Bot</b>

Привет!  Бот успешно работает на Railway!

<b>Доступные команды:</b>
/start - главное меню
/help - помощь

 <i>Railway Deploy v1.0</i>"""
        
        await update.message.reply_text(welcome_message, parse_mode='HTML')
        print(' Ответ отправлен успешно')
    except Exception as e:
        print(f' Ошибка отправки ответа: {e}')
        logger.error(f'Error sending response: {e}')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """ <b>Помощь</b>

<b>Команды:</b>
/start - запуск бота
/help - эта справка

 Бот работает на Railway Platform"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')

def main():
    print(' Запуск IT English бота на Railway...')
    
    if not TOKEN:
        print(' BOT_TOKEN не найден!')
        return
    
    try:
        # Создание приложения
        application = Application.builder().token(TOKEN).build()
        print(' Приложение создано')
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', help_command))
        print(' Обработчики команд добавлены')
        
        print(' Запуск polling...')
        print('-' * 50)
        
        # Запуск бота
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message']
        )
        
    except Exception as e:
        print(f' Критическая ошибка: {e}')
        logger.error(f'Critical error: {e}')

if __name__ == '__main__':
    main()
