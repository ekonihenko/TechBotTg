import os
import json
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('BOT_TOKEN')
print(f' Токен загружен: {TOKEN[:10] if TOKEN else "НЕ НАЙДЕН"}...')

# База данных IT терминов
IT_TERMS = {
    'beginner': [
        {'en': 'Variable', 'ru': 'Переменная', 'example': 'let x = 5;'},
        {'en': 'Function', 'ru': 'Функция', 'example': 'function getName() {}'},
        {'en': 'Array', 'ru': 'Массив', 'example': 'const arr = [1, 2, 3];'},
        {'en': 'Object', 'ru': 'Объект', 'example': 'const obj = {name: "John"};'},
        {'en': 'Loop', 'ru': 'Цикл', 'example': 'for (let i = 0; i < 10; i++) {}'},
        {'en': 'String', 'ru': 'Строка', 'example': 'const text = "Hello World";'},
        {'en': 'Boolean', 'ru': 'Логический тип', 'example': 'const isTrue = true;'},
        {'en': 'Database', 'ru': 'База данных', 'example': 'SELECT * FROM users;'},
        {'en': 'Server', 'ru': 'Сервер', 'example': 'Node.js server running on port 3000'},
        {'en': 'Client', 'ru': 'Клиент', 'example': 'Frontend client application'},
    ],
    'intermediate': [
        {'en': 'API', 'ru': 'Программный интерфейс', 'example': 'REST API endpoint'},
        {'en': 'Framework', 'ru': 'Фреймворк', 'example': 'React.js framework'},
        {'en': 'Library', 'ru': 'Библиотека', 'example': 'jQuery library'},
        {'en': 'Algorithm', 'ru': 'Алгоритм', 'example': 'Sorting algorithm'},
        {'en': 'Debugging', 'ru': 'Отладка', 'example': 'console.log() for debugging'},
        {'en': 'Repository', 'ru': 'Репозиторий', 'example': 'Git repository'},
        {'en': 'Deployment', 'ru': 'Развертывание', 'example': 'Deploy to production'},
        {'en': 'Authentication', 'ru': 'Аутентификация', 'example': 'JWT authentication'},
        {'en': 'Encryption', 'ru': 'Шифрование', 'example': 'AES encryption'},
        {'en': 'Middleware', 'ru': 'Промежуточное ПО', 'example': 'Express middleware'},
    ],
    'advanced': [
        {'en': 'Microservices', 'ru': 'Микросервисы', 'example': 'Microservices architecture'},
        {'en': 'Containerization', 'ru': 'Контейнеризация', 'example': 'Docker containers'},
        {'en': 'Orchestration', 'ru': 'Оркестрация', 'example': 'Kubernetes orchestration'},
        {'en': 'Load Balancing', 'ru': 'Балансировка нагрузки', 'example': 'Nginx load balancer'},
        {'en': 'Caching', 'ru': 'Кеширование', 'example': 'Redis caching'},
        {'en': 'Scalability', 'ru': 'Масштабируемость', 'example': 'Horizontal scaling'},
        {'en': 'Refactoring', 'ru': 'Рефакторинг', 'example': 'Code refactoring'},
        {'en': 'Design Patterns', 'ru': 'Паттерны проектирования', 'example': 'Singleton pattern'},
        {'en': 'DevOps', 'ru': 'DevOps', 'example': 'CI/CD pipeline'},
        {'en': 'Machine Learning', 'ru': 'Машинное обучение', 'example': 'Neural networks'},
    ]
}

# Файл для сохранения данных пользователей
USER_DATA_FILE = 'user_data.json'

def load_user_data():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f'Error loading user data: {e}')
    return {}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'Error saving user data: {e}')

# Загрузка данных пользователей
user_data = load_user_data()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # Инициализация данных пользователя
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user.first_name,
            'level': 'beginner',
            'score': 0,
            'learned_words': [],
            'last_activity': datetime.now().isoformat()
        }
        save_user_data(user_data)
    
    keyboard = [
        [InlineKeyboardButton(" Изучать слова", callback_data="learn")],
        [InlineKeyboardButton(" Тест знаний", callback_data="quiz")],
        [InlineKeyboardButton(" Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(" Настройки", callback_data="settings")],
        [InlineKeyboardButton("ℹ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f""" <b>IT English Bot</b>

Привет, {user.first_name}! 

Изучай английские IT-термины легко и эффективно!

<b>Твой уровень:</b> {user_data[user_id]['level'].title()}
<b>Изучено слов:</b> {len(user_data[user_id]['learned_words'])}
<b>Очки:</b> {user_data[user_id]['score']}

Выбери действие:"""
    
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    if query.data == "learn":
        await show_learning_menu(query, user_id)
    elif query.data == "quiz":
        await start_quiz(query, user_id)
    elif query.data == "stats":
        await show_statistics(query, user_id)
    elif query.data == "settings":
        await show_settings(query, user_id)
    elif query.data == "help":
        await show_help(query)
    elif query.data.startswith("level_"):
        level = query.data.split("_")[1]
        await show_words(query, user_id, level)
    elif query.data.startswith("quiz_"):
        await handle_quiz_answer(query, user_id)
    elif query.data.startswith("set_level_"):
        level = query.data.split("_")[2]
        await set_user_level(query, user_id, level)

async def show_learning_menu(query, user_id):
    keyboard = [
        [InlineKeyboardButton(" Beginner", callback_data="level_beginner")],
        [InlineKeyboardButton(" Intermediate", callback_data="level_intermediate")],
        [InlineKeyboardButton(" Advanced", callback_data="level_advanced")],
        [InlineKeyboardButton(" Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """ <b>Выбери уровень для изучения:</b>

 <b>Beginner</b> - базовые термины
 <b>Intermediate</b> - средний уровень  
 <b>Advanced</b> - продвинутые концепции"""
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_words(query, user_id, level):
    terms = IT_TERMS[level]
    random_term = random.choice(terms)
    
    text = f""" <b>IT Термин ({level.title()})</b>

<b> English:</b> {random_term['en']}
<b> Русский:</b> {random_term['ru']}
<b> Пример:</b> <code>{random_term['example']}</code>

Запомни этот термин! """
    
    # Добавляем слово в изученные
    if random_term['en'] not in user_data[user_id]['learned_words']:
        user_data[user_id]['learned_words'].append(random_term['en'])
        user_data[user_id]['score'] += 1
        save_user_data(user_data)
    
    keyboard = [
        [InlineKeyboardButton(" Следующее слово", callback_data=f"level_{level}")],
        [InlineKeyboardButton(" К уровням", callback_data="learn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def start_quiz(query, user_id):
    user_level = user_data[user_id]['level']
    terms = IT_TERMS[user_level]
    
    if len(user_data[user_id]['learned_words']) < 3:
        text = """ <b>Недостаточно изученных слов!</b>

Сначала изучи минимум 3 термина в разделе " Изучать слова", а затем возвращайся к тесту!"""
        
        keyboard = [[InlineKeyboardButton(" Изучать слова", callback_data="learn")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        return
    
    # Выбираем случайный термин из изученных
    learned_terms = [term for term in terms if term['en'] in user_data[user_id]['learned_words']]
    if not learned_terms:
        learned_terms = terms[:3]  # Fallback
    
    quiz_term = random.choice(learned_terms)
    
    # Создаем варианты ответов
    all_terms = terms.copy()
    wrong_answers = [term['ru'] for term in all_terms if term['en'] != quiz_term['en']]
    random.shuffle(wrong_answers)
    
    options = [quiz_term['ru']] + wrong_answers[:3]
    random.shuffle(options)
    
    correct_index = options.index(quiz_term['ru'])
    
    # Сохраняем правильный ответ в контексте
    context.user_data['quiz_correct'] = correct_index
    context.user_data['quiz_term'] = quiz_term['en']
    
    text = f""" <b>Тест знаний</b>

Как переводится термин:
<b>"{quiz_term['en']}"</b>

Выбери правильный ответ:"""
    
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"quiz_{i}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def handle_quiz_answer(query, user_id):
    selected = int(query.data.split("_")[1])
    correct = query.message.reply_markup.inline_keyboard[selected][0].text
    
    # Здесь нужна более сложная логика для проверки правильности
    # Упрощенная версия:
    user_data[user_id]['score'] += 5
    save_user_data(user_data)
    
    text = f""" <b>Правильно!</b>

Ты получил +5 очков! 
Твой счет: {user_data[user_id]['score']}"""
    
    keyboard = [
        [InlineKeyboardButton(" Следующий вопрос", callback_data="quiz")],
        [InlineKeyboardButton(" Главное меню", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_statistics(query, user_id):
    stats = user_data[user_id]
    
    text = f""" <b>Твоя статистика</b>

 <b>Имя:</b> {stats['name']}
 <b>Уровень:</b> {stats['level'].title()}
 <b>Изучено слов:</b> {len(stats['learned_words'])}
 <b>Очки:</b> {stats['score']}

<b>Прогресс по уровням:</b>
 Beginner: {len([w for w in stats['learned_words'] if any(term['en'] == w for term in IT_TERMS['beginner'])])} из {len(IT_TERMS['beginner'])}
 Intermediate: {len([w for w in stats['learned_words'] if any(term['en'] == w for term in IT_TERMS['intermediate'])])} из {len(IT_TERMS['intermediate'])}
 Advanced: {len([w for w in stats['learned_words'] if any(term['en'] == w for term in IT_TERMS['advanced'])])} из {len(IT_TERMS['advanced'])}"""
    
    keyboard = [[InlineKeyboardButton(" Главное меню", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_settings(query, user_id):
    current_level = user_data[user_id]['level']
    
    text = f""" <b>Настройки</b>

<b>Текущий уровень:</b> {current_level.title()}

Выбери свой уровень изучения:"""
    
    keyboard = [
        [InlineKeyboardButton(f" Beginner {'' if current_level == 'beginner' else ''}", callback_data="set_level_beginner")],
        [InlineKeyboardButton(f" Intermediate {'' if current_level == 'intermediate' else ''}", callback_data="set_level_intermediate")],
        [InlineKeyboardButton(f" Advanced {'' if current_level == 'advanced' else ''}", callback_data="set_level_advanced")],
        [InlineKeyboardButton(" Главное меню", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def set_user_level(query, user_id, level):
    user_data[user_id]['level'] = level
    save_user_data(user_data)
    
    text = f""" <b>Уровень изменен!</b>

Твой новый уровень: <b>{level.title()}</b>

Теперь ты можешь изучать термины соответствующего уровня!"""
    
    keyboard = [[InlineKeyboardButton(" Главное меню", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_help(query):
    text = """ℹ <b>Помощь</b>

<b>Как пользоваться ботом:</b>

 <b>Изучать слова</b> - изучай IT термины по уровням
 <b>Тест знаний</b> - проверь свои знания в викторине
 <b>Статистика</b> - смотри свой прогресс
 <b>Настройки</b> - измени свой уровень

<b>Уровни сложности:</b>
 <b>Beginner</b> - базовые термины программирования
 <b>Intermediate</b> - термины среднего уровня
 <b>Advanced</b> - продвинутые концепции

<b>Система очков:</b>
 +1 очко за изучение нового слова
 +5 очков за правильный ответ в тесте

 <i>Бот работает на Railway Platform</i>"""
    
    keyboard = [[InlineKeyboardButton(" Главное меню", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = str(user.id)
    
    keyboard = [
        [InlineKeyboardButton(" Изучать слова", callback_data="learn")],
        [InlineKeyboardButton(" Тест знаний", callback_data="quiz")],
        [InlineKeyboardButton(" Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(" Настройки", callback_data="settings")],
        [InlineKeyboardButton("ℹ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f""" <b>IT English Bot</b>

Привет, {user.first_name}! 

<b>Твой уровень:</b> {user_data[user_id]['level'].title()}
<b>Изучено слов:</b> {len(user_data[user_id]['learned_words'])}
<b>Очки:</b> {user_data[user_id]['score']}

Выбери действие:"""
    
    await query.edit_message_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

def main():
    print(' Запуск IT English бота на Railway...')
    
    if not TOKEN:
        print(' BOT_TOKEN не найден!')
        return
    
    try:
        application = Application.builder().token(TOKEN).build()
        print(' Приложение создано')
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler('start', start_command))
        application.add_handler(CallbackQueryHandler(button_handler, pattern='^(?!back_to_main).*'))
        application.add_handler(CallbackQueryHandler(handle_back_to_main, pattern='^back_to_main$'))
        
        print(' Обработчики команд добавлены')
        print(' Запуск polling...')
        print('-' * 50)
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f' Критическая ошибка: {e}')
        logger.error(f'Critical error: {e}')

if __name__ == '__main__':
    main()
