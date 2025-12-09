import os
import json
import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "1256727972"  #  ВАШ TELEGRAM ID ДЛЯ АДМИНКИ

print(f' Токен загружен: {TOKEN[:10] if TOKEN else "НЕ НАЙДЕН"}...')
print(f' Админ ID установлен: {ADMIN_ID}')

#  ЭМОДЗИ И ИКОНКИ
ICONS = {
    'categories': {
        'popular_it': '',
        'daily_phrases': '', 
        'qa_testing': '',
        'python_terms': ''
    },
    'actions': {
        'learn': '',
        'quiz': '',
        'stats': '',
        'help': 'ℹ',
        'back': '',
        'next': '',
        'correct': '',
        'wrong': '',
        'new': '',
        'fire': '',
        'star': '',
        'trophy': '',
        'medal_gold': '',
        'medal_silver': '', 
        'medal_bronze': '',
        'rocket': '',
        'brain': '',
        'party': '',
        'target': '',
        'chart': '',
        'users': '',
        'crown': '',
        'admin': '',
        'refresh': ''
    }
}

#  РАСШИРЕННАЯ БАЗА ДАННЫХ IT ТЕРМИНОВ
IT_KNOWLEDGE_BASE = {
    'popular_it': [
        {'en': 'Variable', 'ru': 'Переменная', 'example': 'let userName = "John";', 'difficulty': 1},
        {'en': 'Function', 'ru': 'Функция', 'example': 'function calculate() { return 5 + 3; }', 'difficulty': 1},
        {'en': 'Array', 'ru': 'Массив', 'example': 'const numbers = [1, 2, 3, 4, 5];', 'difficulty': 1},
        {'en': 'Object', 'ru': 'Объект', 'example': 'const user = {name: "Alice", age: 25};', 'difficulty': 1},
        {'en': 'String', 'ru': 'Строка', 'example': 'const message = "Hello World";', 'difficulty': 1},
        {'en': 'Boolean', 'ru': 'Логический тип', 'example': 'const isActive = true;', 'difficulty': 1},
        {'en': 'Loop', 'ru': 'Цикл', 'example': 'for (let i = 0; i < 10; i++) {}', 'difficulty': 2},
        {'en': 'Condition', 'ru': 'Условие', 'example': 'if (x > 5) { console.log("Big"); }', 'difficulty': 2},
        {'en': 'Database', 'ru': 'База данных', 'example': 'SELECT * FROM users WHERE age > 18;', 'difficulty': 2},
        {'en': 'Server', 'ru': 'Сервер', 'example': 'Express server running on port 3000', 'difficulty': 2},
        {'en': 'Client', 'ru': 'Клиент', 'example': 'Frontend React client application', 'difficulty': 2},
        {'en': 'API', 'ru': 'Программный интерфейс', 'example': 'GET /api/users - REST API endpoint', 'difficulty': 3},
        {'en': 'Framework', 'ru': 'Фреймворк', 'example': 'React.js - JavaScript framework', 'difficulty': 3},
        {'en': 'Library', 'ru': 'Библиотека', 'example': 'Lodash - utility library', 'difficulty': 3},
        {'en': 'Algorithm', 'ru': 'Алгоритм', 'example': 'Quick sort algorithm', 'difficulty': 3},
        {'en': 'Bug', 'ru': 'Ошибка/Баг', 'example': 'Found a bug in the login function', 'difficulty': 1},
        {'en': 'Debug', 'ru': 'Отладка', 'example': 'console.log() for debugging', 'difficulty': 2},
        {'en': 'Deploy', 'ru': 'Развертывание', 'example': 'Deploy application to production', 'difficulty': 3},
        {'en': 'Repository', 'ru': 'Репозиторий', 'example': 'Git repository on GitHub', 'difficulty': 2},
        {'en': 'Version', 'ru': 'Версия', 'example': 'Application version 2.1.0', 'difficulty': 1}
    ],
    'daily_phrases': [
        {'en': 'Daily standup', 'ru': 'Ежедневная планерка', 'example': 'We have daily standup at 9 AM', 'difficulty': 2},
        {'en': 'Sprint planning', 'ru': 'Планирование спринта', 'example': 'Sprint planning meeting tomorrow', 'difficulty': 2},
        {'en': 'Code review', 'ru': 'Ревью кода', 'example': 'Please do code review for my PR', 'difficulty': 2},
        {'en': 'Pull request', 'ru': 'Запрос на слияние', 'example': 'Created a pull request for new feature', 'difficulty': 2},
        {'en': 'Merge conflict', 'ru': 'Конфликт слияния', 'example': 'Resolve merge conflict in main branch', 'difficulty': 3},
        {'en': 'Hotfix', 'ru': 'Срочное исправление', 'example': 'Need to deploy hotfix ASAP', 'difficulty': 2},
        {'en': 'Rollback', 'ru': 'Откат изменений', 'example': 'Rollback to previous version', 'difficulty': 2},
        {'en': 'Deployment', 'ru': 'Развертывание', 'example': 'Deployment scheduled for Friday', 'difficulty': 2},
        {'en': 'Production', 'ru': 'Продакшн/Боевая среда', 'example': 'Bug found in production environment', 'difficulty': 2},
        {'en': 'Staging', 'ru': 'Тестовая среда', 'example': 'Test on staging before production', 'difficulty': 2},
        {'en': 'Feature flag', 'ru': 'Флаг функции', 'example': 'Enable feature flag for beta users', 'difficulty': 3},
        {'en': 'Technical debt', 'ru': 'Технический долг', 'example': 'We need to address technical debt', 'difficulty': 3},
        {'en': 'Refactoring', 'ru': 'Рефакторинг', 'example': 'Code refactoring improves readability', 'difficulty': 3},
        {'en': 'Pair programming', 'ru': 'Парное программирование', 'example': 'Lets do pair programming session', 'difficulty': 2},
        {'en': 'Backlog', 'ru': 'Бэклог/Список задач', 'example': 'Add new task to product backlog', 'difficulty': 2},
        {'en': 'User story', 'ru': 'Пользовательская история', 'example': 'Write user story for login feature', 'difficulty': 2},
        {'en': 'Acceptance criteria', 'ru': 'Критерии приемки', 'example': 'Define acceptance criteria clearly', 'difficulty': 3},
        {'en': 'Definition of done', 'ru': 'Критерии готовности', 'example': 'Task meets definition of done', 'difficulty': 3},
        {'en': 'Retrospective', 'ru': 'Ретроспектива', 'example': 'Sprint retrospective meeting', 'difficulty': 2},
        {'en': 'Blocker', 'ru': 'Блокер/Препятствие', 'example': 'API issue is a blocker for frontend', 'difficulty': 2}
    ],
    'qa_testing': [
        {'en': 'Test case', 'ru': 'Тест-кейс', 'example': 'Write test case for login functionality', 'difficulty': 1},
        {'en': 'Test suite', 'ru': 'Набор тестов', 'example': 'Run full test suite before release', 'difficulty': 2},
        {'en': 'Unit test', 'ru': 'Модульный тест', 'example': 'Unit test for calculateTotal function', 'difficulty': 2},
        {'en': 'Integration test', 'ru': 'Интеграционный тест', 'example': 'Integration test for API endpoints', 'difficulty': 3},
        {'en': 'End-to-end test', 'ru': 'Сквозной тест', 'example': 'E2E test for user registration flow', 'difficulty': 3},
        {'en': 'Smoke test', 'ru': 'Дымовой тест', 'example': 'Smoke test after deployment', 'difficulty': 2},
        {'en': 'Regression test', 'ru': 'Регрессионный тест', 'example': 'Regression test for bug fixes', 'difficulty': 2},
        {'en': 'Performance test', 'ru': 'Тест производительности', 'example': 'Performance test shows slow response', 'difficulty': 3},
        {'en': 'Load test', 'ru': 'Нагрузочный тест', 'example': 'Load test with 1000 concurrent users', 'difficulty': 3},
        {'en': 'Stress test', 'ru': 'Стресс-тест', 'example': 'Stress test to find breaking point', 'difficulty': 3},
        {'en': 'Mock', 'ru': 'Заглушка/Мок', 'example': 'Mock API response for testing', 'difficulty': 2},
        {'en': 'Stub', 'ru': 'Заглушка', 'example': 'Create stub for external service', 'difficulty': 2},
        {'en': 'Test data', 'ru': 'Тестовые данные', 'example': 'Prepare test data for scenarios', 'difficulty': 1},
        {'en': 'Test environment', 'ru': 'Тестовая среда', 'example': 'Deploy to test environment first', 'difficulty': 1},
        {'en': 'Bug report', 'ru': 'Отчет об ошибке', 'example': 'Submit detailed bug report', 'difficulty': 1},
        {'en': 'Test coverage', 'ru': 'Покрытие тестами', 'example': 'Achieve 80% test coverage', 'difficulty': 2},
        {'en': 'False positive', 'ru': 'Ложное срабатывание', 'example': 'Test shows false positive result', 'difficulty': 3},
        {'en': 'False negative', 'ru': 'Ложное отрицание', 'example': 'Bug missed - false negative', 'difficulty': 3},
        {'en': 'Test automation', 'ru': 'Автоматизация тестирования', 'example': 'Implement test automation framework', 'difficulty': 3},
        {'en': 'Continuous testing', 'ru': 'Непрерывное тестирование', 'example': 'Continuous testing in CI/CD pipeline', 'difficulty': 3}
    ],
    'python_terms': [
        {'en': 'List comprehension', 'ru': 'Генератор списков', 'example': '[x**2 for x in range(10)]', 'difficulty': 3},
        {'en': 'Dictionary', 'ru': 'Словарь', 'example': 'user = {"name": "John", "age": 30}', 'difficulty': 1},
        {'en': 'Tuple', 'ru': 'Кортеж', 'example': 'coordinates = (10, 20)', 'difficulty': 1},
        {'en': 'Set', 'ru': 'Множество', 'example': 'unique_numbers = {1, 2, 3, 4}', 'difficulty': 2},
        {'en': 'Lambda function', 'ru': 'Лямбда-функция', 'example': 'square = lambda x: x**2', 'difficulty': 3},
        {'en': 'Decorator', 'ru': 'Декоратор', 'example': '@property def name(self): return self._name', 'difficulty': 3},
        {'en': 'Generator', 'ru': 'Генератор', 'example': 'def count(): yield 1; yield 2', 'difficulty': 3},
        {'en': 'Iterator', 'ru': 'Итератор', 'example': 'for item in my_iterator:', 'difficulty': 2},
        {'en': 'Class', 'ru': 'Класс', 'example': 'class User: def __init__(self, name):', 'difficulty': 2},
        {'en': 'Inheritance', 'ru': 'Наследование', 'example': 'class Admin(User): pass', 'difficulty': 2},
        {'en': 'Method', 'ru': 'Метод', 'example': 'def get_name(self): return self.name', 'difficulty': 1},
        {'en': 'Property', 'ru': 'Свойство', 'example': '@property def full_name(self):', 'difficulty': 2},
        {'en': 'Module', 'ru': 'Модуль', 'example': 'import datetime', 'difficulty': 1},
        {'en': 'Package', 'ru': 'Пакет', 'example': 'from mypackage import mymodule', 'difficulty': 2},
        {'en': 'Exception', 'ru': 'Исключение', 'example': 'try: ... except ValueError:', 'difficulty': 2},
        {'en': 'Context manager', 'ru': 'Контекстный менеджер', 'example': 'with open("file.txt") as f:', 'difficulty': 3},
        {'en': 'List slicing', 'ru': 'Срезы списков', 'example': 'numbers[1:5] # elements 1 to 4', 'difficulty': 2},
        {'en': 'String formatting', 'ru': 'Форматирование строк', 'example': 'f"Hello, {name}!"', 'difficulty': 2},
        {'en': 'Virtual environment', 'ru': 'Виртуальное окружение', 'example': 'python -m venv myenv', 'difficulty': 2},
        {'en': 'PIP package', 'ru': 'PIP пакет', 'example': 'pip install requests', 'difficulty': 1}
    ]
}

# Файлы для сохранения данных
USER_DATA_FILE = 'user_progress.json'
GLOBAL_STATS_FILE = 'global_stats.json'

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

def load_global_stats():
    try:
        if os.path.exists(GLOBAL_STATS_FILE):
            with open(GLOBAL_STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f'Error loading global stats: {e}')
    return {
        'total_users': 0,
        'active_today': 0,
        'total_terms_learned': 0,
        'total_quizzes_completed': 0,
        'popular_categories': {},
        'daily_stats': {},
        'bot_started': datetime.now().isoformat()
    }

def save_global_stats(stats):
    try:
        with open(GLOBAL_STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'Error saving global stats: {e}')

def update_global_stats(action, category=None, user_id=None):
    stats = load_global_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today not in stats['daily_stats']:
        stats['daily_stats'][today] = {
            'active_users': [],
            'terms_learned': 0,
            'quizzes_completed': 0
        }
    
    # Добавляем пользователя в активные за сегодня
    if user_id and user_id not in stats['daily_stats'][today]['active_users']:
        stats['daily_stats'][today]['active_users'].append(user_id)
    
    if action == 'new_user':
        stats['total_users'] += 1
    elif action == 'term_learned':
        stats['total_terms_learned'] += 1
        stats['daily_stats'][today]['terms_learned'] += 1
        if category:
            stats['popular_categories'][category] = stats['popular_categories'].get(category, 0) + 1
    elif action == 'quiz_completed':
        stats['total_quizzes_completed'] += 1
        stats['daily_stats'][today]['quizzes_completed'] += 1
    
    save_global_stats(stats)

# Загрузка данных
user_data = load_user_data()
global_stats = load_global_stats()

def init_user(user_id, user_name):
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user_name,
            'current_category': 'popular_it',
            'score': 0,
            'learned_terms': {
                'popular_it': [],
                'daily_phrases': [],
                'qa_testing': [],
                'python_terms': []
            },
            'quiz_stats': {
                'correct': 0,
                'total': 0,
                'streak': 0,
                'best_streak': 0
            },
            'achievements': [],
            'join_date': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        save_user_data(user_data)
        update_global_stats('new_user', user_id=user_id)
    
    # Обновляем последнюю активность
    user_data[user_id]['last_activity'] = datetime.now().isoformat()
    update_global_stats('activity', user_id=user_id)
    return user_data[user_id]

def get_difficulty_icon(difficulty):
    if difficulty == 1:
        return ''  # Легкий
    elif difficulty == 2:
        return ''  # Средний
    else:
        return ''  # Сложный

def get_user_level(total_learned):
    if total_learned >= 60:
        return {'name': 'Эксперт', 'icon': ICONS['actions']['medal_gold']}
    elif total_learned >= 30:
        return {'name': 'Продвинутый', 'icon': ICONS['actions']['medal_silver']}
    elif total_learned >= 10:
        return {'name': 'Изучающий', 'icon': ICONS['actions']['medal_bronze']}
    else:
        return {'name': 'Новичок', 'icon': ''}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # Инициализация пользователя
    user_profile = init_user(user_id, user.first_name)
    
    keyboard = [
        [InlineKeyboardButton(f"{ICONS['actions']['learn']} Изучать термины", callback_data="categories")],
        [InlineKeyboardButton(f"{ICONS['actions']['quiz']} Тест знаний", callback_data="quiz_menu")],
        [InlineKeyboardButton(f"{ICONS['actions']['stats']} Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(f"{ICONS['actions']['help']} Помощь", callback_data="help")]
    ]
    
    #  АДМИНСКАЯ КНОПКА ДЛЯ ВАС!
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton(f"{ICONS['actions']['crown']} Админ панель", callback_data="admin")])
        print(f' Админ {user.first_name} ({user_id}) подключился!')
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    total_learned = sum(len(terms) for terms in user_profile['learned_terms'].values())
    user_level = get_user_level(total_learned)
    accuracy = round(user_profile['quiz_stats']['correct']/max(user_profile['quiz_stats']['total'], 1)*100)
    
    welcome_text = f"""{ICONS['actions']['rocket']} <b>IT English Bot - Полная версия</b>

Привет, {user.first_name}! {ICONS['actions']['party']}

{ICONS['actions']['fire']} <b>База знаний: 80 терминов!</b>
{ICONS['categories']['popular_it']} Популярные IT термины
{ICONS['categories']['daily_phrases']} Фразы с дейликов  
{ICONS['categories']['qa_testing']} Автотестирование
{ICONS['categories']['python_terms']} Python термины

{ICONS['actions']['chart']} <b>Твой прогресс:</b>
{user_level['icon']} Уровень: {user_level['name']}
{ICONS['actions']['brain']} Изучено: {total_learned}/80 терминов
{ICONS['actions']['star']} Очки: {user_profile['score']}
{ICONS['actions']['target']} Точность: {accuracy}%
{ICONS['actions']['fire']} Лучшая серия: {user_profile['quiz_stats']['best_streak']}

Выбери действие:"""
    
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_profile = user_data.get(user_id, {})
    
    if query.data == "categories":
        await show_categories(query, user_id)
    elif query.data == "quiz_menu":
        await show_quiz_menu(query, user_id)
    elif query.data == "stats":
        await show_statistics(query, user_id)
    elif query.data == "help":
        await show_help(query)
    elif query.data == "admin" and user_id == ADMIN_ID:
        await show_admin_panel(query)
    elif query.data.startswith("category_"):
        category = query.data.split("_", 1)[1]
        await show_terms(query, user_id, category)
    elif query.data.startswith("quiz_"):
        category = query.data.split("_", 1)[1]
        await start_quiz(query, user_id, category, context)
    elif query.data.startswith("answer_"):
        await handle_quiz_answer(query, user_id, context)
    elif query.data == "back_main":
        await back_to_main(query, user_id)

async def show_categories(query, user_id):
    user_profile = user_data[user_id]
    
    categories = {
        'popular_it': {'name': 'Популярные IT', 'icon': ICONS['categories']['popular_it']},
        'daily_phrases': {'name': 'Фразы с дейликов', 'icon': ICONS['categories']['daily_phrases']},
        'qa_testing': {'name': 'Автотестирование', 'icon': ICONS['categories']['qa_testing']},
        'python_terms': {'name': 'Python термины', 'icon': ICONS['categories']['python_terms']}
    }
    
    keyboard = []
    for cat_id, cat_info in categories.items():
        learned_count = len(user_profile['learned_terms'][cat_id])
        total_count = len(IT_KNOWLEDGE_BASE[cat_id])
        progress_percentage = round(learned_count / total_count * 100)
        
        keyboard.append([InlineKeyboardButton(
            f"{cat_info['icon']} {cat_info['name']} ({learned_count}/{total_count}) {progress_percentage}%", 
            callback_data=f"category_{cat_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(f"{ICONS['actions']['back']} Главное меню", callback_data="back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""{ICONS['actions']['learn']} <b>Выбери категорию для изучения:</b>

{ICONS['categories']['popular_it']} <b>Популярные IT</b> - основные термины программирования
{ICONS['categories']['daily_phrases']} <b>Фразы с дейликов</b> - повседневное общение в команде
{ICONS['categories']['qa_testing']} <b>Автотестирование</b> - QA и тестирование  
{ICONS['categories']['python_terms']} <b>Python термины</b> - специфика Python

{ICONS['actions']['star']} <i>В скобках показан прогресс изучения</i>"""
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_terms(query, user_id, category):
    user_profile = user_data[user_id]
    terms = IT_KNOWLEDGE_BASE[category]
    
    # Выбираем случайный термин
    random_term = random.choice(terms)
    
    # Добавляем в изученные если еще нет
    is_new = False
    if random_term['en'] not in user_profile['learned_terms'][category]:
        user_profile['learned_terms'][category].append(random_term['en'])
        user_profile['score'] += 2
        user_profile['last_activity'] = datetime.now().isoformat()
        save_user_data(user_data)
        update_global_stats('term_learned', category, user_id)
        is_new = True
    
    category_names = {
        'popular_it': f"{ICONS['categories']['popular_it']} Популярные IT",
        'daily_phrases': f"{ICONS['categories']['daily_phrases']} Фразы с дейликов",
        'qa_testing': f"{ICONS['categories']['qa_testing']} Автотестирование",
        'python_terms': f"{ICONS['categories']['python_terms']} Python термины"
    }
    
    difficulty_icon = get_difficulty_icon(random_term['difficulty'])
    new_badge = f" {ICONS['actions']['new']}" if is_new else ""
    points_text = f"\n\n{ICONS['actions']['party']} <b>+2 очка за новый термин!</b>" if is_new else ""
    
    text = f"""{ICONS['actions']['learn']} <b>{category_names[category]}{new_badge}</b>

{difficulty_icon} <b>Сложность:</b> {"Легкий" if random_term['difficulty'] == 1 else "Средний" if random_term['difficulty'] == 2 else "Сложный"}

<b> English:</b> {random_term['en']}
<b> Русский:</b> {random_term['ru']}
<b> Пример:</b> <code>{random_term['example']}</code>

{ICONS['actions']['brain']} <i>Запомни этот термин!</i>{points_text}"""
    
    keyboard = [
        [InlineKeyboardButton(f"{ICONS['actions']['next']} Следующий термин", callback_data=f"category_{category}")],
        [InlineKeyboardButton(f"{ICONS['actions']['quiz']} Тест по категории", callback_data=f"quiz_{category}")],
        [InlineKeyboardButton(f"{ICONS['actions']['back']} К категориям", callback_data="categories")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_quiz_menu(query, user_id):
    user_profile = user_data[user_id]
    
    categories = {
        'popular_it': {'name': 'Популярные IT', 'icon': ICONS['categories']['popular_it']},
        'daily_phrases': {'name': 'Фразы с дейликов', 'icon': ICONS['categories']['daily_phrases']},
        'qa_testing': {'name': 'Автотестирование', 'icon': ICONS['categories']['qa_testing']},
        'python_terms': {'name': 'Python термины', 'icon': ICONS['categories']['python_terms']}
    }
    
    keyboard = []
    available_categories = 0
    
    for cat_id, cat_info in categories.items():
        learned_count = len(user_profile['learned_terms'][cat_id])
        if learned_count >= 3:  # Минимум 3 термина для теста
            keyboard.append([InlineKeyboardButton(
                f"{cat_info['icon']} {cat_info['name']} ({learned_count} терминов)", 
                callback_data=f"quiz_{cat_id}"
            )])
            available_categories += 1
    
    if available_categories == 0:
        text = f"""{ICONS['actions']['wrong']} <b>Недостаточно изученных терминов!</b>

Для прохождения теста нужно изучить минимум 3 термина в любой категории.

{ICONS['actions']['learn']} Начни с изучения терминов!"""
        
        keyboard = [[InlineKeyboardButton(f"{ICONS['actions']['learn']} Изучать термины", callback_data="categories")]]
    else:
        streak_text = f"\n{ICONS['actions']['fire']} Текущая серия: {user_profile['quiz_stats']['streak']}" if user_profile['quiz_stats']['streak'] > 0 else ""
        
        text = f"""{ICONS['actions']['quiz']} <b>Выбери категорию для теста:</b>

Доступны только категории с изученными терминами (минимум 3).

{ICONS['actions']['star']} <i>За правильный ответ +5 очков!</i>
{ICONS['actions']['fire']} <i>Собирай серии правильных ответов!</i>{streak_text}"""
    
    keyboard.append([InlineKeyboardButton(f"{ICONS['actions']['back']} Главное меню", callback_data="back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def start_quiz(query, user_id, category, context):
    user_profile = user_data[user_id]
    terms = IT_KNOWLEDGE_BASE[category]
    learned_terms = user_profile['learned_terms'][category]
    
    if len(learned_terms) < 3:
        await query.answer("Изучи больше терминов для теста!", show_alert=True)
        return
    
    # Выбираем случайный изученный термин
    available_terms = [term for term in terms if term['en'] in learned_terms]
    quiz_term = random.choice(available_terms)
    
    # Создаем варианты ответов из той же категории
    all_terms = terms.copy()
    wrong_answers = [term['ru'] for term in all_terms if term['en'] != quiz_term['en']]
    random.shuffle(wrong_answers)
    
    # Берем 3 неправильных ответа
    options = [quiz_term['ru']] + wrong_answers[:3]
    random.shuffle(options)
    
    correct_index = options.index(quiz_term['ru'])
    
    # Сохраняем данные квиза в контексте пользователя
    context.user_data[f'quiz_correct_{user_id}'] = correct_index
    context.user_data[f'quiz_term_{user_id}'] = quiz_term['en']
    context.user_data[f'quiz_category_{user_id}'] = category
    context.user_data[f'quiz_correct_answer_{user_id}'] = quiz_term['ru']
    
    category_names = {
        'popular_it': f"{ICONS['categories']['popular_it']} Популярные IT",
        'daily_phrases': f"{ICONS['categories']['daily_phrases']} Фразы с дейликов", 
        'qa_testing': f"{ICONS['categories']['qa_testing']} Автотестирование",
        'python_terms': f"{ICONS['categories']['python_terms']} Python термины"
    }
    
    difficulty_icon = get_difficulty_icon(quiz_term['difficulty'])
    
    text = f"""{ICONS['actions']['quiz']} <b>Тест: {category_names[category]}</b>

{difficulty_icon} Как переводится термин:
<b>"{quiz_term['en']}"</b>

{ICONS['actions']['target']} Выбери правильный ответ:"""
    
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"answer_{i}")])
    
    keyboard.append([InlineKeyboardButton(f"{ICONS['actions']['back']} К тестам", callback_data="quiz_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def handle_quiz_answer(query, user_id, context):
    selected = int(query.data.split("_")[1])
    
    # Получаем сохраненные данные квиза
    correct_index = context.user_data.get(f'quiz_correct_{user_id}', 0)
    quiz_term = context.user_data.get(f'quiz_term_{user_id}', '')
    correct_answer = context.user_data.get(f'quiz_correct_answer_{user_id}', '')
    
    user_profile = user_data[user_id]
    user_profile['quiz_stats']['total'] += 1
    
    is_correct = selected == correct_index
    
    if is_correct:
        user_profile['quiz_stats']['correct'] += 1
        user_profile['quiz_stats']['streak'] += 1
        user_profile['score'] += 5
        
        # Обновляем лучшую серию
        if user_profile['quiz_stats']['streak'] > user_profile['quiz_stats']['best_streak']:
            user_profile['quiz_stats']['best_streak'] = user_profile['quiz_stats']['streak']
        
        streak_bonus = ""
        if user_profile['quiz_stats']['streak'] >= 5:
            bonus_points = user_profile['quiz_stats']['streak']
            user_profile['score'] += bonus_points
            streak_bonus = f"\n{ICONS['actions']['fire']} <b>Бонус за серию: +{bonus_points} очков!</b>"
        
        text = f"""{ICONS['actions']['correct']} <b>Правильно!</b>

{ICONS['actions']['party']} Отлично! <b>"{quiz_term}" = "{correct_answer}"</b>
{ICONS['actions']['star']} <b>+5 очков!</b>
{ICONS['actions']['fire']} Серия правильных ответов: {user_profile['quiz_stats']['streak']}{streak_bonus}

{ICONS['actions']['chart']} Твой счет: {user_profile['score']} очков
{ICONS['actions']['target']} Точность: {user_profile['quiz_stats']['correct']}/{user_profile['quiz_stats']['total']} ({round(user_profile['quiz_stats']['correct']/user_profile['quiz_stats']['total']*100)}%)"""
    else:
        user_profile['quiz_stats']['streak'] = 0  # Сбрасываем серию
        
        text = f"""{ICONS['actions']['wrong']} <b>Неправильно!</b>

{ICONS['actions']['brain']} Правильный ответ: <b>"{quiz_term}" = "{correct_answer}"</b>
 Не расстраивайся, продолжай учиться!

{ICONS['actions']['chart']} Твой счет: {user_profile['score']} очков  
{ICONS['actions']['target']} Точность: {user_profile['quiz_stats']['correct']}/{user_profile['quiz_stats']['total']} ({round(user_profile['quiz_stats']['correct']/user_profile['quiz_stats']['total']*100)}%)"""
    
    save_user_data(user_data)
    update_global_stats('quiz_completed', user_id=user_id)
    
    keyboard = [
        [InlineKeyboardButton(f"{ICONS['actions']['quiz']} Следующий вопрос", callback_data="quiz_menu")],
        [InlineKeyboardButton(f"{ICONS['actions']['learn']} Изучать термины", callback_data="categories")],
        [InlineKeyboardButton(f"{ICONS['actions']['back']} Главное меню", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_statistics(query, user_id):
    user_profile = user_data[user_id]
    
    total_learned = sum(len(terms) for terms in user_profile['learned_terms'].values())
    total_available = sum(len(terms) for terms in IT_KNOWLEDGE_BASE.values())
    user_level = get_user_level(total_learned)
    
    categories_stats = []
    for cat_id, cat_terms in user_profile['learned_terms'].items():
        cat_names = {
            'popular_it': f"{ICONS['categories']['popular_it']} Популярные IT",
            'daily_phrases': f"{ICONS['categories']['daily_phrases']} Дейлики",
            'qa_testing': f"{ICONS['categories']['qa_testing']} Тестирование", 
            'python_terms': f"{ICONS['categories']['python_terms']} Python"
        }
        learned = len(cat_terms)
        total = len(IT_KNOWLEDGE_BASE[cat_id])
        percentage = round(learned/total*100) if total > 0 else 0
        progress_bar = "" * (learned * 10 // total) + "" * (10 - learned * 10 // total)
        categories_stats.append(f"{cat_names[cat_id]}: {learned}/{total} ({percentage}%)\n{progress_bar}")
    
    accuracy = round(user_profile['quiz_stats']['correct']/max(user_profile['quiz_stats']['total'], 1)*100)
    
    # Достижения
    achievements = []
    if total_learned >= 10:
        achievements.append(" Первые 10 терминов")
    if total_learned >= 50:
        achievements.append(" Полсотни терминов")
    if user_profile['quiz_stats']['best_streak'] >= 5:
        achievements.append(" Серия из 5 ответов")
    if accuracy >= 80 and user_profile['quiz_stats']['total'] >= 10:
        achievements.append(" Меткий стрелок")
    
    achievements_text = "\n".join(achievements) if achievements else "Пока нет достижений"
    
    text = f"""{ICONS['actions']['stats']} <b>Статистика {user_profile['name']}</b>

{user_level['icon']} <b>Уровень:</b> {user_level['name']}
{ICONS['actions']['brain']} <b>Изучено терминов:</b> {total_learned}/{total_available}
{ICONS['actions']['star']} <b>Набрано очков:</b> {user_profile['score']}
{ICONS['actions']['quiz']} <b>Тестов пройдено:</b> {user_profile['quiz_stats']['total']}
{ICONS['actions']['target']} <b>Точность ответов:</b> {accuracy}%
{ICONS['actions']['fire']} <b>Лучшая серия:</b> {user_profile['quiz_stats']['best_streak']}

{ICONS['actions']['chart']} <b>Прогресс по категориям:</b>
{chr(10).join(categories_stats)}

{ICONS['actions']['trophy']} <b>Достижения:</b>
{achievements_text}

{ICONS['actions']['users']} <i>Присоединился: {user_profile['join_date'][:10]}</i>"""
    
    keyboard = [[InlineKeyboardButton(f"{ICONS['actions']['back']} Главное меню", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_admin_panel(query):
    stats = load_global_stats()
    
    # Подсчитываем активных пользователей сегодня
    today = datetime.now().strftime('%Y-%m-%d')
    today_stats = stats['daily_stats'].get(today, {})
    active_today = len(today_stats.get('active_users', []))
    
    # Топ категории
    popular_cats = sorted(stats['popular_categories'].items(), 
                         key=lambda x: x[1], reverse=True)[:3]
    
    top_categories = []
    cat_names = {
        'popular_it': f"{ICONS['categories']['popular_it']} IT",
        'daily_phrases': f"{ICONS['categories']['daily_phrases']} Дейлики",
        'qa_testing': f"{ICONS['categories']['qa_testing']} Тестирование",
        'python_terms': f"{ICONS['categories']['python_terms']} Python"
    }
    
    for cat, count in popular_cats:
        if cat in cat_names:
            top_categories.append(f"{cat_names[cat]}: {count}")
    
    top_cats_text = "\n".join(top_categories) if top_categories else "Нет данных"
    
    # Статистика за последние 7 дней
    week_stats = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_data = stats['daily_stats'].get(date, {})
        terms = day_data.get('terms_learned', 0)
        quizzes = day_data.get('quizzes_completed', 0)
        active_users = len(day_data.get('active_users', []))
        week_stats.append(f"{date}: {active_users} польз., {terms} терм., {quizzes} тест.")
    
    week_text = "\n".join(week_stats)
    
    # Топ пользователи по очкам
    top_users = sorted(user_data.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
    top_users_text = []
    for i, (uid, profile) in enumerate(top_users, 1):
        medal = ['', '', '', '4', '5'][i-1]
        top_users_text.append(f"{medal} {profile['name']}: {profile['score']} очков")
    
    top_users_str = "\n".join(top_users_text) if top_users_text else "Нет данных"
    
    text = f"""{ICONS['actions']['crown']} <b>Админ панель</b>

{ICONS['actions']['users']} <b>Пользователи:</b>
 Всего зарегистрировано: {stats['total_users']}
 Активны сегодня: {active_today}
 Всего в базе: {len(user_data)}

{ICONS['actions']['chart']} <b>Общая активность:</b>
 Изучено терминов: {stats['total_terms_learned']}
 Пройдено тестов: {stats['total_quizzes_completed']}

{ICONS['actions']['fire']} <b>Популярные категории:</b>
{top_cats_text}

{ICONS['actions']['trophy']} <b>Топ пользователей:</b>
{top_users_str}

{ICONS['actions']['target']} <b>Активность за неделю:</b>
{week_text}

{ICONS['actions']['rocket']} <i>Бот запущен: {stats.get('bot_started', 'N/A')[:10]}</i>"""
    
    keyboard = [
        [InlineKeyboardButton(f"{ICONS['actions']['refresh']} Обновить", callback_data="admin")],
        [InlineKeyboardButton(f"{ICONS['actions']['back']} Главное меню", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_help(query):
    text = f"""{ICONS['actions']['help']} <b>IT English Bot - Помощь</b>

{ICONS['actions']['rocket']} <b>Возможности бота:</b>

{ICONS['actions']['learn']} <b>Изучение терминов</b>
 80 терминов в 4 категориях
 +2 очка за каждый новый термин
 Примеры использования с кодом
 Уровни сложности: 

{ICONS['actions']['quiz']} <b>Тестирование</b>
 Тесты по изученным терминам
 +5 очков за правильный ответ
 Система серий и бонусов
 Статистика точности

{ICONS['actions']['stats']} <b>Прогресс и достижения</b>
 Отслеживание изученных терминов
 Система очков и уровней
 Достижения за прогресс
 Детальная статистика

{ICONS['actions']['fire']} <b>Система серий:</b>
 Собирай серии правильных ответов
 Бонусные очки за длинные серии
 Отслеживание лучшей серии

{ICONS['categories']['popular_it']} <b>Популярные IT</b> - основы программирования
{ICONS['categories']['daily_phrases']} <b>Дейлики</b> - повседневное общение в команде
{ICONS['categories']['qa_testing']} <b>Тестирование</b> - QA и автотесты
{ICONS['categories']['python_terms']} <b>Python</b> - специфические термины Python

{ICONS['actions']['trophy']} <b>Система уровней:</b>
 Новичок: 0-9 терминов
{ICONS['actions']['medal_bronze']} Изучающий: 10-29 терминов
{ICONS['actions']['medal_silver']} Продвинутый: 30-59 терминов  
{ICONS['actions']['medal_gold']} Эксперт: 60+ терминов

{ICONS['actions']['rocket']} <i>Полная версия на Railway Platform</i>"""
    
    keyboard = [[InlineKeyboardButton(f"{ICONS['actions']['back']} Главное меню", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def back_to_main(query, user_id):
    user = query.from_user
    user_profile = user_data[user_id]
    
    keyboard = [
        [InlineKeyboardButton(f"{ICONS['actions']['learn']} Изучать термины", callback_data="categories")],
        [InlineKeyboardButton(f"{ICONS['actions']['quiz']} Тест знаний", callback_data="quiz_menu")],
        [InlineKeyboardButton(f"{ICONS['actions']['stats']} Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(f"{ICONS['actions']['help']} Помощь", callback_data="help")]
    ]
    
    #  АДМИНСКАЯ КНОПКА ДЛЯ ВАС!
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton(f"{ICONS['actions']['crown']} Админ панель", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    total_learned = sum(len(terms) for terms in user_profile['learned_terms'].values())
    user_level = get_user_level(total_learned)
    accuracy = round(user_profile['quiz_stats']['correct']/max(user_profile['quiz_stats']['total'], 1)*100)
    
    welcome_text = f"""{ICONS['actions']['rocket']} <b>IT English Bot</b>

Привет, {user.first_name}! {ICONS['actions']['party']}

{ICONS['actions']['chart']} <b>Твой прогресс:</b>
{user_level['icon']} Уровень: {user_level['name']}
{ICONS['actions']['brain']} Изучено: {total_learned}/80 терминов
{ICONS['actions']['star']} Очки: {user_profile['score']}
{ICONS['actions']['target']} Точность: {accuracy}%

Выбери действие:"""
    
    await query.edit_message_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

def main():
    print(' Запуск улучшенного IT English бота...')
    print(' С красивыми иконками и полным функционалом!')
    print(' Статистика пользователей включена')
    print(f' Админ ID: {ADMIN_ID}')
    
    if not TOKEN:
        print(' BOT_TOKEN не найден!')
        return
    
    try:
        application = Application.builder().token(TOKEN).build()
        print(' Приложение создано')
        
        application.add_handler(CommandHandler('start', start_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        print(' Обработчики зарегистрированы')
        print(' Запуск polling...')
        print('=' * 60)
        print(' УЛУЧШЕННЫЙ IT ENGLISH БОТ ЗАПУЩЕН!')
        print(' Красивые иконки и интерфейс')
        print(' Исправленная система тестов') 
        print(' Статистика пользователей')
        print(' Админ. панель с полной аналитикой')
        print(' Система достижений')
        print(' Серии правильных ответов')
        print('=' * 60)
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f' Критическая ошибка: {e}')
        logger.error(f'Critical error: {e}')

if __name__ == '__main__':
    main()
