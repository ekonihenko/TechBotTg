import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения Railway
TOKEN = os.getenv('BOT_TOKEN')
print(f' Токен загружен: {TOKEN[:10] if TOKEN else "НЕ НАЙДЕН"}...')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f' Команда /start от пользователя {user.id}')
    
    keyboard = [
        [InlineKeyboardButton(" Изучать слова", callback_data="learn")],
        [InlineKeyboardButton(" Тест знаний", callback_data="quiz")],
        [InlineKeyboardButton(" Моя статистика", callback_data="stats")],
        [InlineKeyboardButton("ℹ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f""" <b>IT English Bot</b>

Привет, {user.first_name}! 

Изучай английские IT-термины легко и эффективно!

<b> Интерактивная версия на Railway!</b>

Выбери действие:"""
    
    try:
        await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
        print(' Интерактивное меню отправлено')
    except Exception as e:
        print(f' Ошибка отправки меню: {e}')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    print(f' Нажата кнопка: {query.data}')
    
    if query.data == "learn":
        text = """ <b>Изучение слов</b>

<b> English:</b> Variable
<b> Русский:</b> Переменная
<b> Пример:</b> <code>let x = 5;</code>

Запомни этот термин! 

<i>Это демо-версия. Полный функционал в разработке.</i>"""
        
        keyboard = [[InlineKeyboardButton(" Главное меню", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        
    elif query.data == "quiz":
        text = """ <b>Тест знаний</b>

Как переводится термин:
<b>"Function"</b>

Выбери правильный ответ:"""
        
        keyboard = [
            [InlineKeyboardButton(" Функция", callback_data="correct")],
            [InlineKeyboardButton(" Переменная", callback_data="wrong")],
            [InlineKeyboardButton(" Массив", callback_data="wrong")],
            [InlineKeyboardButton(" Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        
    elif query.data == "stats":
        text = f""" <b>Твоя статистика</b>

 <b>Имя:</b> {query.from_user.first_name}
 <b>Уровень:</b> Beginner
 <b>Изучено слов:</b> 5
 <b>Очки:</b> 25

<b>Прогресс по уровням:</b>
 Beginner: 5 из 10
 Intermediate: 0 из 10  
 Advanced: 0 из 10

<i>Статистика сохраняется локально</i>"""
        
        keyboard = [[InlineKeyboardButton(" Главное меню", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        
    elif query.data == "help":
        text = """ℹ <b>Помощь</b>

<b>Как пользоваться ботом:</b>

 <b>Изучать слова</b> - изучай IT термины по уровням
 <b>Тест знаний</b> - проверь свои знания в викторине  
 <b>Статистика</b> - смотри свой прогресс

<b>Уровни сложности:</b>
 <b>Beginner</b> - базовые термины
 <b>Intermediate</b> - средний уровень
 <b>Advanced</b> - продвинутые концепции

 <i>Бот работает на Railway Platform</i>
 <i>Версия: Interactive Demo v1.0</i>"""
        
        keyboard = [[InlineKeyboardButton(" Главное меню", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        
    elif query.data == "correct":
        text = """ <b>Правильно!</b>

Отличная работа! 
Function = Функция

<b>Ты получил +5 очков!</b>

<i>В полной версии очки сохраняются</i>"""
        
        keyboard = [
            [InlineKeyboardButton(" Следующий вопрос", callback_data="quiz")],
            [InlineKeyboardButton(" Главное меню", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        
    elif query.data == "wrong":
        text = """ <b>Неправильно!</b>

Правильный ответ: <b>Функция</b>

Function = Функция
Попробуй запомнить! 

<i>Не расстраивайся, продолжай учиться!</i>"""
        
        keyboard = [
            [InlineKeyboardButton(" Попробовать снова", callback_data="quiz")],
            [InlineKeyboardButton(" Главное меню", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        
    elif query.data == "back":
        await start_command_callback(query)

async def start_command_callback(query):
    user = query.from_user
    
    keyboard = [
        [InlineKeyboardButton(" Изучать слова", callback_data="learn")],
        [InlineKeyboardButton(" Тест знаний", callback_data="quiz")],
        [InlineKeyboardButton(" Моя статистика", callback_data="stats")],
        [InlineKeyboardButton("ℹ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f""" <b>IT English Bot</b>

Привет, {user.first_name}! 

<b> Интерактивная версия работает!</b>

Выбери действие:"""
    
    await query.edit_message_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

def main():
    print(' Запуск IT English бота на Railway...')
    print(f' Python версия: {os.sys.version}')
    
    if not TOKEN:
        print(' BOT_TOKEN не найден в переменных окружения!')
        return
    
    try:
        print(' Создание приложения...')
        application = Application.builder().token(TOKEN).build()
        print(' Приложение создано успешно')
        
        print(' Регистрация обработчиков...')
        application.add_handler(CommandHandler('start', start_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        print(' Обработчики зарегистрированы')
        
        print(' Запуск polling...')
        print('=' * 50)
        print(' БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!')
        print('=' * 50)
        
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
        
    except Exception as e:
        print(f' Критическая ошибка при запуске: {e}')
        logger.error(f'Critical startup error: {e}', exc_info=True)

if __name__ == '__main__':
    main()
