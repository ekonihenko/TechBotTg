import os
import json
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
print(f'📱 Токен загружен: {TOKEN[:10] if TOKEN else "НЕ НАЙДЕН"}...')

# База данных терминов
TERMS_DATABASE = [
    {'en': 'backbone', 'ru': 'основа, опора, суть; магистраль', 'example_en': 'This server is the backbone of our network', 'example_ru': 'Этот сервер - основа нашей сети'},
    {'en': 'capability', 'ru': 'возможность, способность; производительность', 'example_en': 'The new system has advanced capabilities', 'example_ru': 'Новая система имеет расширенные возможности'},
    {'en': 'concise', 'ru': 'краткий; сжатый; недолговременный', 'example_en': 'Please write a concise report', 'example_ru': 'Пожалуйста, напишите краткий отчет'},
    {'en': 'deploy', 'ru': 'вводить в действие, разворачивать', 'example_en': 'We need to deploy the new version', 'example_ru': 'Нам нужно развернуть новую версию'},
    {'en': 'discard', 'ru': 'отбрасывать, отвергать; не учитывать', 'example_en': 'The system will discard invalid data', 'example_ru': 'Система отбросит недействительные данные'},
    {'en': 'disposal', 'ru': 'освобождение', 'example_en': 'Proper disposal of old equipment is important', 'example_ru': 'Правильная утилизация старого оборудования важна'},
    {'en': 'drastic', 'ru': 'глубокий; крутой; форсированный', 'example_en': 'We need drastic changes in our approach', 'example_ru': 'Нам нужны кардинальные изменения в подходе'},
    {'en': 'facilitate', 'ru': 'облегчать, способствовать, помогать', 'example_en': 'This tool will facilitate the development process', 'example_ru': 'Этот инструмент облегчит процесс разработки'},
    {'en': 'inclined', 'ru': 'расположенный, предрасположенный, склонный', 'example_en': 'I am inclined to agree with this solution', 'example_ru': 'Я склонен согласиться с этим решением'},
    {'en': 'mainstay', 'ru': 'главная поддержка, опора, оплот', 'example_en': 'Java is the mainstay of our backend', 'example_ru': 'Java - основа нашего бэкенда'},
    {'en': 'omission', 'ru': 'опускание; вычеркивание', 'example_en': 'The omission of this feature was intentional', 'example_ru': 'Исключение этой функции было намеренным'},
    {'en': 'shredder', 'ru': 'шредер, машинка для уничтожения бумаг', 'example_en': 'Use the paper shredder for confidential documents', 'example_ru': 'Используйте шредер для конфиденциальных документов'},
    {'en': 'unify', 'ru': 'унифицировать; выполнять операцию унификации', 'example_en': 'We need to unify all interfaces', 'example_ru': 'Нам нужно унифицировать все интерфейсы'},
    {'en': 'airfare', 'ru': 'стоимость авиаперелета, цена авиабилета', 'example_en': 'The airfare to the conference is expensive', 'example_ru': 'Стоимость перелета на конференцию высокая'},
    {'en': 'attendee', 'ru': 'участник (конференции, семинара)', 'example_en': 'Each attendee will receive a welcome package', 'example_ru': 'Каждый участник получит приветственный пакет'},
    {'en': 'clock up', 'ru': 'отмечать пройденное расстояние; записывать в актив', 'example_en': 'I clocked up 40 hours of coding this week', 'example_ru': 'Я отработал 40 часов программирования на этой неделе'},
    {'en': 'dip toe', 'ru': 'макать, окунать (палец ноги)', 'example_en': 'Let me dip my toe into machine learning', 'example_ru': 'Позвольте мне попробовать машинное обучение'},
    {'en': 'downturn', 'ru': 'спад (деловой активности); понижение', 'example_en': 'The market downturn affected our sales', 'example_ru': 'Спад рынка повлиял на наши продажи'},
    {'en': 'eliminate', 'ru': 'устранять, исключать', 'example_en': 'This update will eliminate the bug', 'example_ru': 'Это обновление устранит ошибку'},
    {'en': 'evangelical', 'ru': 'евангелический', 'example_en': 'He is evangelical about clean code', 'example_ru': 'Он фанатично относится к чистому коду'},
    {'en': 'flock', 'ru': 'стекаться; приходить толпой', 'example_en': 'Developers flock to this new framework', 'example_ru': 'Разработчики стекаются к этому новому фреймворку'},
    {'en': 'forge', 'ru': 'постепенно выходить на первое место; лидировать', 'example_en': 'Our team will forge ahead with the project', 'example_ru': 'Наша команда будет продвигаться вперед с проектом'},
    {'en': 'implosion', 'ru': 'уменьшение, сокращение; обвал, фиаско', 'example_en': 'The startup faced an implosion after funding ran out', 'example_ru': 'Стартап столкнулся с крахом после исчерпания финансирования'},
    {'en': 'plug insurance', 'ru': 'рекламировать (страхование)', 'example_en': 'The company plugs its insurance products heavily', 'example_ru': 'Компания активно рекламирует свои страховые продукты'},
    {'en': 'recession', 'ru': 'рецессия, спад', 'example_en': 'The tech industry survived the recession', 'example_ru': 'IT-индустрия пережила рецессию'},
    {'en': 'standpoint', 'ru': 'позиция, точка зрения', 'example_en': 'From a security standpoint, this is risky', 'example_ru': 'С точки зрения безопасности это рискованно'},
    {'en': 'tactile', 'ru': 'осязательный, тактильный; осязаемый', 'example_en': 'The new interface provides tactile feedback', 'example_ru': 'Новый интерфейс обеспечивает тактильную обратную связь'},
    {'en': 'alongside', 'ru': 'неподалеку, поблизости; рядом', 'example_en': 'Work alongside experienced developers', 'example_ru': 'Работайте рядом с опытными разработчиками'},
    {'en': 'broadband', 'ru': 'широкополосный; широкополосная сеть', 'example_en': 'Broadband internet connection is required', 'example_ru': 'Требуется широкополосное интернет-соединение'},
    {'en': 'chassis', 'ru': 'шасси; ходовая часть', 'example_en': 'The server chassis holds multiple drives', 'example_ru': 'Шасси сервера содержит несколько дисков'},
    {'en': 'erroneous', 'ru': 'ошибочный', 'example_en': 'The erroneous data caused system failure', 'example_ru': 'Ошибочные данные вызвали сбой системы'},
    {'en': 'prior to', 'ru': 'прежде чем; до, перед, раньше', 'example_en': 'Test the code prior to deployment', 'example_ru': 'Протестируйте код перед развертыванием'},
    {'en': 'set-up', 'ru': 'структура, устройство (организации)', 'example_en': 'The current set-up works well for our team', 'example_ru': 'Текущая структура хорошо работает для нашей команды'},
    {'en': 'stock system', 'ru': 'система ассортимента (товаров)', 'example_en': 'Our stock system tracks inventory automatically', 'example_ru': 'Наша система учета товаров автоматически отслеживает запасы'},
    {'en': 'terrestrial aerial', 'ru': 'наземная антенна', 'example_en': 'The terrestrial aerial receives digital signals', 'example_ru': 'Наземная антенна принимает цифровые сигналы'},
    {'en': 'time-shift', 'ru': 'сдвигать во времени', 'example_en': 'We can time-shift the meeting to accommodate everyone', 'example_ru': 'Мы можем перенести встречу, чтобы всем было удобно'},
    {'en': 'vast', 'ru': 'обширный, огромный, широкий', 'example_en': 'The database contains vast amounts of data', 'example_ru': 'База данных содержит огромные объемы данных'},
    {'en': 'weld', 'ru': 'сваривать, соединять', 'example_en': 'We need to weld these components together', 'example_ru': 'Нам нужно сварить эти компоненты вместе'},
    {'en': 'aptitude', 'ru': 'склонность, способность', 'example_en': 'She shows great aptitude for programming', 'example_ru': 'Она проявляет большие способности к программированию'},
    {'en': 'chime', 'ru': 'соответствовать, звучать согласно', 'example_en': 'Your ideas chime with our company vision', 'example_ru': 'Ваши идеи соответствуют видению нашей компании'},
    {'en': 'curriculum', 'ru': 'курс обучения, учебный план', 'example_en': 'The programming curriculum includes Python and Java', 'example_ru': 'Учебная программа по программированию включает Python и Java'},
    {'en': 'daunt', 'ru': 'пугать, обескураживать', 'example_en': 'Don\'t let complex algorithms daunt you', 'example_ru': 'Не позволяйте сложным алгоритмам пугать вас'},
    {'en': 'debug', 'ru': 'отлаживать (программу)', 'example_en': 'I need to debug this code', 'example_ru': 'Мне нужно отладить этот код'},
    {'en': 'disrepute', 'ru': 'дурная слава, плохая репутация', 'example_en': 'The company fell into disrepute after the scandal', 'example_ru': 'Компания приобрела дурную славу после скандала'},
    {'en': 'get to grips', 'ru': 'понимать, разбираться, справляться', 'example_en': 'I need to get to grips with this new technology', 'example_ru': 'Мне нужно разобраться с этой новой технологией'},
    {'en': 'groundswell', 'ru': 'волна, растущая общественная поддержка', 'example_en': 'There\'s a groundswell of support for open source', 'example_ru': 'Растет волна поддержки открытого исходного кода'},
    {'en': 'overdo', 'ru': 'перестараться, переусердствовать; преувеличивать', 'example_en': 'Don\'t overdo the optimization', 'example_ru': 'Не переусердствуйте с оптимизацией'},
    {'en': 'pecking order', 'ru': 'неофициальная иерархия; порядок подчинения', 'example_en': 'Understanding the pecking order is important in any team', 'example_ru': 'Понимание иерархии важно в любой команде'},
    {'en': 'prosper', 'ru': 'благоденствовать, преуспевать, процветать', 'example_en': 'The startup began to prosper after the investment', 'example_ru': 'Стартап начал процветать после инвестиций'},
    {'en': 'spark', 'ru': 'вызывать, становиться причиной', 'example_en': 'This innovation will spark new opportunities', 'example_ru': 'Эта инновация вызовет новые возможности'},
    {'en': 'teething troubles', 'ru': 'первоначальные затруднения', 'example_en': 'Every new system has teething troubles', 'example_ru': 'У каждой новой системы есть начальные проблемы'},
    {'en': 'unambiguous', 'ru': 'однозначный, недвусмысленный', 'example_en': 'The requirements must be unambiguous', 'example_ru': 'Требования должны быть однозначными'},
    {'en': 'clerical', 'ru': 'конторский, канцелярский', 'example_en': 'Automate clerical tasks to save time', 'example_ru': 'Автоматизируйте канцелярские задачи для экономии времени'},
    {'en': 'deem', 'ru': 'полагать, считать', 'example_en': 'We deem this approach most suitable', 'example_ru': 'Мы считаем этот подход наиболее подходящим'},
    {'en': 'drudgery', 'ru': 'тяжелая, монотонная работа', 'example_en': 'Automation eliminates the drudgery of manual tasks', 'example_ru': 'Автоматизация устраняет рутину ручных задач'},
    {'en': 'frumpy', 'ru': 'старомодный', 'example_en': 'The old interface looks frumpy now', 'example_ru': 'Старый интерфейс теперь выглядит устаревшим'},
    {'en': 'grotty', 'ru': 'безобразный; никуда не годный', 'example_en': 'This grotty code needs refactoring', 'example_ru': 'Этот ужасный код нуждается в рефакторинге'},
    {'en': 'interminable', 'ru': 'бесконечный, беспредельный', 'example_en': 'The interminable loading time frustrates users', 'example_ru': 'Бесконечное время загрузки расстраивает пользователей'},
    {'en': 'keystroke', 'ru': 'нажатие клавиши или кнопки', 'example_en': 'Every keystroke is logged for security', 'example_ru': 'Каждое нажатие клавиши регистрируется для безопасности'},
    {'en': 'paste', 'ru': 'вставлять (данные из буфера обмена)', 'example_en': 'Copy and paste the code snippet', 'example_ru': 'Скопируйте и вставьте фрагмент кода'},
    {'en': 'rewire', 'ru': 'перекоммутировать', 'example_en': 'We need to rewire the network connections', 'example_ru': 'Нам нужно переподключить сетевые соединения'},
    {'en': 'skive', 'ru': 'увиливать, уклоняться (от работы); сачковать', 'example_en': 'Don\'t skive off during important meetings', 'example_ru': 'Не увиливайте от важных встреч'},
    {'en': 'subservient', 'ru': 'подчиненный, зависимый; рабский', 'example_en': 'The API is subservient to the main application', 'example_ru': 'API подчинен основному приложению'},
    {'en': 'surreptitious', 'ru': 'тайный; сделанный тайком', 'example_en': 'Surreptitious data collection is unethical', 'example_ru': 'Тайный сбор данных неэтичен'},
    {'en': 'tedium', 'ru': 'скука; утомительность', 'example_en': 'Automation reduces the tedium of repetitive tasks', 'example_ru': 'Автоматизация снижает скуку повторяющихся задач'},
    {'en': 'tot up', 'ru': 'суммировать', 'example_en': 'Tot up all the expenses for the project', 'example_ru': 'Подсчитайте все расходы по проекту'},
    {'en': 'valve', 'ru': '(электронная) лампа', 'example_en': 'Old computers used vacuum tubes and valves', 'example_ru': 'Старые компьютеры использовали электронные лампы'},
    {'en': 'whir', 'ru': 'жужжать', 'example_en': 'The hard drive whirs when accessing data', 'example_ru': 'Жесткий диск жужжит при обращении к данным'},
    {'en': 'whizzy', 'ru': 'продвинутый, на базе инновационных технологий', 'example_en': 'This whizzy new app has great features', 'example_ru': 'Это продвинутое новое приложение имеет отличные функции'},
    {'en': 'wizardry', 'ru': 'магия, волшебство', 'example_en': 'The code optimization was pure wizardry', 'example_ru': 'Оптимизация кода была настоящим волшебством'},
    {'en': 'assign', 'ru': 'поручать', 'example_en': 'Assign this task to the junior developer', 'example_ru': 'Поручите эту задачу младшему разработчику'},
    {'en': 'colon', 'ru': 'двоеточие', 'example_en': 'Use a colon before the list items', 'example_ru': 'Используйте двоеточие перед элементами списка'},
    {'en': 'compliance', 'ru': 'согласие, соответствие', 'example_en': 'The system meets security compliance standards', 'example_ru': 'Система соответствует стандартам безопасности'},
    {'en': 'data breach', 'ru': 'повреждение, нарушение данных', 'example_en': 'The data breach exposed customer information', 'example_ru': 'Утечка данных раскрыла информацию о клиентах'},
    {'en': 'detect malware', 'ru': 'обнаруживать вредоносное ПО', 'example_en': 'The antivirus can detect malware effectively', 'example_ru': 'Антивирус может эффективно обнаруживать вредоносное ПО'},
    {'en': 'disseminate', 'ru': 'распространять', 'example_en': 'We need to disseminate this information quickly', 'example_ru': 'Нам нужно быстро распространить эту информацию'},
    {'en': 'encompass', 'ru': 'охватывать, включать', 'example_en': 'The project encompasses multiple technologies', 'example_ru': 'Проект охватывает множество технологий'},
    {'en': 'exceedingly', 'ru': 'чрезвычайно, очень', 'example_en': 'The performance is exceedingly good', 'example_ru': 'Производительность чрезвычайно хорошая'},
    {'en': 'influx', 'ru': 'наплыв, приток', 'example_en': 'There was an influx of new users', 'example_ru': 'Был наплыв новых пользователей'},
    {'en': 'juggle', 'ru': 'совмещать', 'example_en': 'I have to juggle multiple projects', 'example_ru': 'Мне приходится совмещать несколько проектов'},
    {'en': 'layperson', 'ru': 'непрофессионал, дилетант', 'example_en': 'Explain it so a layperson can understand', 'example_ru': 'Объясните так, чтобы непрофессионал понял'},
    {'en': 'oversee', 'ru': 'наблюдать, контролировать', 'example_en': 'The manager will oversee the development', 'example_ru': 'Менеджер будет контролировать разработку'},
    {'en': 'patch', 'ru': 'латать, ставить заплату', 'example_en': 'We need to patch the security vulnerability', 'example_ru': 'Нам нужно исправить уязвимость безопасности'},
    {'en': 'tangible', 'ru': 'реальный, ощутимый', 'example_en': 'We need tangible results from this project', 'example_ru': 'Нам нужны ощутимые результаты от этого проекта'},
    {'en': 'be at stake', 'ru': 'находиться под угрозой', 'example_en': 'The company\'s reputation is at stake', 'example_ru': 'Репутация компании находится под угрозой'},
    {'en': 'vendor', 'ru': 'поставщик, производитель, продавец', 'example_en': 'Choose a reliable software vendor', 'example_ru': 'Выберите надежного поставщика программного обеспечения'},
    {'en': 'vulnerability', 'ru': 'уязвимость, ранимость', 'example_en': 'The security scan found several vulnerabilities', 'example_ru': 'Сканирование безопасности обнаружило несколько уязвимостей'},
    {'en': 'accountability', 'ru': 'подотчетность, возможность идентификации', 'example_en': 'There must be accountability for system failures', 'example_ru': 'Должна быть подотчетность за сбои системы'},
    {'en': 'chunk', 'ru': 'порция, кусок программы; участок памяти', 'example_en': 'Process the data in small chunks', 'example_ru': 'Обрабатывайте данные небольшими порциями'},
    {'en': 'cost-effective', 'ru': 'эффективный по затратам, рентабельный', 'example_en': 'This solution is more cost-effective', 'example_ru': 'Это решение более рентабельно'},
    {'en': 'cursory', 'ru': 'поверхностный, беглый', 'example_en': 'A cursory review revealed several issues', 'example_ru': 'Беглый обзор выявил несколько проблем'},
    {'en': 'customized', 'ru': 'заказной, изготовленный по техническим условиям', 'example_en': 'We offer customized software solutions', 'example_ru': 'Мы предлагаем индивидуальные программные решения'},
    {'en': 'deficiency', 'ru': 'нехватка, дефицит', 'example_en': 'There\'s a deficiency in our testing process', 'example_ru': 'В нашем процессе тестирования есть недостатки'},
    {'en': 'detractor', 'ru': 'инсинуатор, клеветник, очернитель', 'example_en': 'Even detractors admit the system works well', 'example_ru': 'Даже критики признают, что система работает хорошо'},
    {'en': 'enhance', 'ru': 'улучшать, доводить', 'example_en': 'This feature will enhance user experience', 'example_ru': 'Эта функция улучшит пользовательский опыт'},
    {'en': 'exhaustively', 'ru': 'исчерпывающе, полностью, совершенно', 'example_en': 'Test the system exhaustively before release', 'example_ru': 'Протестируйте систему исчерпывающе перед выпуском'},
    {'en': 'feasibility', 'ru': 'осуществимость, выполнимость', 'example_en': 'We need to check the feasibility of this approach', 'example_ru': 'Нам нужно проверить осуществимость этого подхода'},
    {'en': 'for awhile', 'ru': 'на (какое-то) время, ненадолго', 'example_en': 'Let\'s pause development for awhile', 'example_ru': 'Давайте приостановим разработку ненадолго'},
    {'en': 'incrementally', 'ru': 'поступательно, шаг за шагом', 'example_en': 'Develop the features incrementally', 'example_ru': 'Разрабатывайте функции поступательно'},
    {'en': 'iterative', 'ru': 'итеративный, итерационный', 'example_en': 'We use an iterative development approach', 'example_ru': 'Мы используем итеративный подход к разработке'},
    {'en': 'linear', 'ru': 'линейный, прямолинейный', 'example_en': 'The algorithm has linear time complexity', 'example_ru': 'Алгоритм имеет линейную временную сложность'},
    {'en': 'maintenance', 'ru': 'обслуживание, содержание', 'example_en': 'Regular maintenance prevents system failures', 'example_ru': 'Регулярное обслуживание предотвращает сбои системы'},
    {'en': 'milestone', 'ru': 'промежуточный этап; контрольная точка', 'example_en': 'We reached an important project milestone', 'example_ru': 'Мы достигли важного этапа проекта'},
    {'en': 'nevertheless', 'ru': 'тем не менее', 'example_en': 'The code is complex, nevertheless it works', 'example_ru': 'Код сложный, тем не менее он работает'},
    {'en': 'novice', 'ru': 'начинающий, новичок', 'example_en': 'This tutorial is perfect for a novice programmer', 'example_ru': 'Этот учебник идеален для начинающего программиста'},
    {'en': 'overlapping', 'ru': 'перекрывающий, частично дублирующий', 'example_en': 'Avoid overlapping responsibilities in the team', 'example_ru': 'Избегайте пересекающихся обязанностей в команде'},
    {'en': 'pitfall', 'ru': 'возможная ошибка, сложность', 'example_en': 'Watch out for common programming pitfalls', 'example_ru': 'Остерегайтесь распространенных ошибок программирования'},
    {'en': 'post-mortem', 'ru': 'вскрытие, обсуждение после окончания', 'example_en': 'We held a post-mortem meeting after the incident', 'example_ru': 'Мы провели разбор полетов после инцидента'},
    {'en': 'proponent', 'ru': 'сторонник, защитник', 'example_en': 'I\'m a strong proponent of clean code', 'example_ru': 'Я сильный сторонник чистого кода'},
    {'en': 'rigid', 'ru': 'жесткий, негибкий', 'example_en': 'The system architecture is too rigid', 'example_ru': 'Архитектура системы слишком жесткая'},
    {'en': 'rigorously', 'ru': 'тщательно', 'example_en': 'Test the application rigorously', 'example_ru': 'Тщательно протестируйте приложение'},
    {'en': 'sequential', 'ru': 'последовательный (процесс)', 'example_en': 'The tasks must be executed in sequential order', 'example_ru': 'Задачи должны выполняться в последовательном порядке'},
    {'en': 'sheer', 'ru': 'абсолютный, полнейший', 'example_en': 'The sheer complexity of the system is overwhelming', 'example_ru': 'Абсолютная сложность системы подавляющая'},
    {'en': 'sloppy', 'ru': 'нестабильный (об источнике питания)', 'example_en': 'Sloppy code leads to bugs', 'example_ru': 'Небрежный код приводит к ошибкам'},
    {'en': 'thorough', 'ru': 'тщательный, доскональный', 'example_en': 'Conduct a thorough code review', 'example_ru': 'Проведите тщательный обзор кода'},
    {'en': 'truism', 'ru': 'трюизм, прописная истина', 'example_en': 'It\'s a truism that good code is self-documenting', 'example_ru': 'Это прописная истина, что хороший код самодокументируется'},
    {'en': 'turn-around', 'ru': 'неожиданное изменение, поворот', 'example_en': 'The project had a complete turn-around', 'example_ru': 'Проект полностью изменил направление'},
    {'en': 'viable', 'ru': 'жизнеспособный', 'example_en': 'This business model is not viable', 'example_ru': 'Эта бизнес-модель нежизнеспособна'},
    {'en': 'amplitude', 'ru': 'амплитуда', 'example_en': 'Measure the signal amplitude', 'example_ru': 'Измерьте амплитуду сигнала'},
    {'en': 'antiquated', 'ru': 'устарелый, архаичный, допотопный', 'example_en': 'The antiquated system needs replacement', 'example_ru': 'Устаревшая система нуждается в замене'},
    {'en': 'array', 'ru': 'множество, спектр, матрица', 'example_en': 'Create an array to store the values', 'example_ru': 'Создайте массив для хранения значений'},
    {'en': 'asynchronous', 'ru': 'асинхронный, несинхронный', 'example_en': 'Use asynchronous programming for better performance', 'example_ru': 'Используйте асинхронное программирование для лучшей производительности'},
    {'en': 'brute force', 'ru': 'решать в лоб / методом грубой силы', 'example_en': 'We used brute force to crack the password', 'example_ru': 'Мы использовали метод грубой силы для взлома пароля'},
    {'en': 'byproduct', 'ru': 'побочный продукт/результат', 'example_en': 'Better documentation was a byproduct of the refactoring', 'example_ru': 'Лучшая документация была побочным результатом рефакторинга'},
    {'en': 'carbon breakdown', 'ru': 'распад/расщепление углерода', 'example_en': 'Carbon breakdown affects the material properties', 'example_ru': 'Распад углерода влияет на свойства материала'},
    {'en': 'circuit', 'ru': 'цепь, электрическая цепь, схема', 'example_en': 'The circuit board controls the device', 'example_ru': 'Печатная плата управляет устройством'},
    {'en': 'compatibility', 'ru': 'совместимость, сочетаемость', 'example_en': 'Check backward compatibility with older versions', 'example_ru': 'Проверьте обратную совместимость со старыми версиями'},
    {'en': 'cutting-edge', 'ru': 'передовой, современный, новейший', 'example_en': 'We use cutting-edge technology', 'example_ru': 'Мы используем передовые технологии'},
    {'en': 'decay', 'ru': 'распадаться, разлагаться', 'example_en': 'The signal will decay over time', 'example_ru': 'Сигнал будет затухать со временем'},
    {'en': 'decoherence', 'ru': 'декогеренция, распад суперпозиционных состояний', 'example_en': 'Quantum decoherence affects computation', 'example_ru': 'Квантовая декогеренция влияет на вычисления'},
    {'en': 'discreet', 'ru': 'дискретный, прерывистый', 'example_en': 'Use discreet values for the parameter', 'example_ru': 'Используйте дискретные значения для параметра'},
    {'en': 'emergent', 'ru': 'новый, возникший, развивающийся', 'example_en': 'AI is an emergent technology', 'example_ru': 'ИИ - это развивающаяся технология'},
    {'en': 'emission', 'ru': 'выброс, выделение теплоты', 'example_en': 'Monitor carbon emissions from the data center', 'example_ru': 'Контролируйте выбросы углерода от центра обработки данных'},
    {'en': 'entanglement', 'ru': 'запутанность; затруднительное положение', 'example_en': 'Quantum entanglement enables secure communication', 'example_ru': 'Квантовая запутанность обеспечивает безопасную связь'},
    {'en': 'equation', 'ru': 'уравнение, формула', 'example_en': 'Solve the mathematical equation', 'example_ru': 'Решите математическое уравнение'},
    {'en': 'excel at', 'ru': 'преуспеть в чём-л.; выполнять особенно хорошо', 'example_en': 'She excels at algorithm design', 'example_ru': 'Она преуспевает в разработке алгоритмов'},
    {'en': 'factor', 'ru': 'разлагать на множители; факторизовать', 'example_en': 'Factor the polynomial equation', 'example_ru': 'Разложите полиномиальное уравнение на множители'},
    {'en': 'fine-tuned', 'ru': 'точно настроенный', 'example_en': 'The algorithm is fine-tuned for performance', 'example_ru': 'Алгоритм точно настроен для производительности'},
    {'en': 'harness', 'ru': 'использовать', 'example_en': 'Harness the power of cloud computing', 'example_ru': 'Используйте мощь облачных вычислений'},
    {'en': 'high-fidelity measurement', 'ru': 'высокоточное измерение', 'example_en': 'We need high-fidelity measurements for accuracy', 'example_ru': 'Нам нужны высокоточные измерения для точности'},
    {'en': 'inaccessible', 'ru': 'недоступный, недостижимый', 'example_en': 'The server is currently inaccessible', 'example_ru': 'Сервер в настоящее время недоступен'},
    {'en': 'laborious', 'ru': 'трудоемкий, трудный', 'example_en': 'Manual testing is laborious and error-prone', 'example_ru': 'Ручное тестирование трудоемко и подвержено ошибкам'},
    {'en': 'maze', 'ru': 'лабиринт, дебри', 'example_en': 'The codebase is a maze of dependencies', 'example_ru': 'Кодовая база - это лабиринт зависимостей'},
    {'en': 'mitigate', 'ru': 'смягчать; уменьшать, снижать', 'example_en': 'Implement measures to mitigate security risks', 'example_ru': 'Внедрите меры для снижения рисков безопасности'},
    {'en': 'output', 'ru': 'выводить, производить, выпускать', 'example_en': 'The function outputs the processed data', 'example_ru': 'Функция выводит обработанные данные'},
    {'en': 'petrochemical', 'ru': 'нефтехимический', 'example_en': 'The petrochemical industry uses advanced software', 'example_ru': 'Нефтехимическая промышленность использует передовое ПО'},
    {'en': 'probabilistically', 'ru': 'вероятностно', 'example_en': 'The algorithm works probabilistically', 'example_ru': 'Алгоритм работает вероятностно'},
    {'en': 'punch-card adders', 'ru': 'сумматоры перфокарт', 'example_en': 'Old computers used punch-card adders', 'example_ru': 'Старые компьютеры использовали сумматоры перфокарт'},
    {'en': 'quantum dots', 'ru': 'квантовые точки', 'example_en': 'Quantum dots improve display technology', 'example_ru': 'Квантовые точки улучшают технологию дисплеев'},
    {'en': 'qubit', 'ru': 'кубит - единица информации в квантовом компьютере', 'example_en': 'Each qubit can be in superposition', 'example_ru': 'Каждый кубит может находиться в суперпозиции'},
    {'en': 'ramp up', 'ru': 'набирать обороты, наращивать', 'example_en': 'We need to ramp up production', 'example_ru': 'Нам нужно наращивать производство'},
    {'en': 'scalability', 'ru': 'масштабируемость, расширяемость', 'example_en': 'The system has excellent scalability', 'example_ru': 'Система имеет отличную масштабируемость'},
    {'en': 'scale', 'ru': 'масштабировать; определять масштаб', 'example_en': 'Scale the application to handle more users', 'example_ru': 'Масштабируйте приложение для обработки большего числа пользователей'},
    {'en': 'semiconductor', 'ru': 'полупроводник, полупроводниковый прибор', 'example_en': 'Semiconductor technology drives computing', 'example_ru': 'Полупроводниковая технология движет вычислениями'},
    {'en': 'speedup', 'ru': 'ускорение; увеличение быстродействия', 'example_en': 'The optimization provided significant speedup', 'example_ru': 'Оптимизация обеспечила значительное ускорение'},
    {'en': 'superconductor development', 'ru': 'разработка сверхпроводников', 'example_en': 'Superconductor development advances quantum computing', 'example_ru': 'Разработка сверхпроводников продвигает квантовые вычисления'},
    {'en': 'accessibility', 'ru': 'доступность', 'example_en': 'Web accessibility is crucial for inclusive design', 'example_ru': 'Веб-доступность критически важна для инклюзивного дизайна'},
    {'en': 'actionable', 'ru': 'действенный', 'example_en': 'Provide actionable feedback to the team', 'example_ru': 'Предоставьте действенную обратную связь команде'},
    {'en': 'adjustable', 'ru': 'регулируемый', 'example_en': 'The interface has adjustable settings', 'example_ru': 'Интерфейс имеет регулируемые настройки'},
    {'en': 'alert', 'ru': 'предупреждать об опасности', 'example_en': 'The system will alert you of any issues', 'example_ru': 'Система предупредит вас о любых проблемах'},
    {'en': 'align with', 'ru': 'соответствовать', 'example_en': 'The design should align with user expectations', 'example_ru': 'Дизайн должен соответствовать ожиданиям пользователей'},
    {'en': 'amenity', 'ru': 'удобства', 'example_en': 'The office has modern amenities', 'example_ru': 'Офис имеет современные удобства'},
    {'en': 'assess', 'ru': 'оценивать', 'example_en': 'Assess the project risks carefully', 'example_ru': 'Тщательно оцените риски проекта'},
    {'en': 'attainable', 'ru': 'достижимый', 'example_en': 'Set attainable goals for the sprint', 'example_ru': 'Поставьте достижимые цели для спринта'},
    {'en': 'bar code', 'ru': 'штрих-код', 'example_en': 'Scan the bar code to get product information', 'example_ru': 'Отсканируйте штрих-код для получения информации о продукте'},
    {'en': 'burglary', 'ru': 'кража со взломом, ограбление', 'example_en': 'Cyber burglary is a growing concern', 'example_ru': 'Кибер-кражи вызывают растущую озабоченность'},
    {'en': 'buzzword', 'ru': 'модное словечко', 'example_en': 'AI is the latest buzzword in tech', 'example_ru': 'ИИ - последнее модное словечко в технологиях'},
    {'en': 'come into picture', 'ru': 'выходить на сцену / на первый план', 'example_en': 'Security concerns come into picture with IoT', 'example_ru': 'Вопросы безопасности выходят на первый план с IoT'},
    {'en': 'computation', 'ru': 'вычисление, процесс вычисления', 'example_en': 'The computation takes several minutes', 'example_ru': 'Вычисление занимает несколько минут'},
    {'en': 'consistent', 'ru': 'согласованный, последовательный', 'example_en': 'Maintain consistent coding standards', 'example_ru': 'Поддерживайте согласованные стандарты кодирования'},
    {'en': 'consumption', 'ru': 'потребление', 'example_en': 'Monitor power consumption of the servers', 'example_ru': 'Контролируйте потребление энергии серверами'},
    {'en': 'contribute to', 'ru': 'способствовать, быть причиной', 'example_en': 'Poor design contributes to user frustration', 'example_ru': 'Плохой дизайн способствует разочарованию пользователей'},
    {'en': 'crucial', 'ru': 'решающий, ключевой', 'example_en': 'Testing is crucial for software quality', 'example_ru': 'Тестирование критически важно для качества ПО'},
    {'en': 'disability', 'ru': 'инвалидность, ограниченные возможности', 'example_en': 'Design for users with disabilities', 'example_ru': 'Проектируйте для пользователей с ограниченными возможностями'},
    {'en': 'era', 'ru': 'эра, эпоха', 'example_en': 'We are entering the era of quantum computing', 'example_ru': 'Мы вступаем в эру квантовых вычислений'},
    {'en': 'evoke', 'ru': 'вызывать', 'example_en': 'The design should evoke trust', 'example_ru': 'Дизайн должен вызывать доверие'},
    {'en': 'font', 'ru': 'шрифт', 'example_en': 'Choose a readable font for the interface', 'example_ru': 'Выберите читаемый шрифт для интерфейса'},
    {'en': 'frustration', 'ru': 'разочарование', 'example_en': 'Poor UX leads to user frustration', 'example_ru': 'Плохой UX приводит к разочарованию пользователей'},
    {'en': 'gaze detection', 'ru': 'распознавание взгляда', 'example_en': 'Gaze detection improves user interaction', 'example_ru': 'Распознавание взгляда улучшает взаимодействие с пользователем'},
    {'en': 'handheld', 'ru': 'портативный, переносной', 'example_en': 'Develop the app for handheld devices', 'example_ru': 'Разработайте приложение для портативных устройств'},
    {'en': 'headphones', 'ru': 'наушники', 'example_en': 'Test audio quality with different headphones', 'example_ru': 'Протестируйте качество звука с разными наушниками'},
    {'en': 'iteratively', 'ru': 'итеративно, многократно', 'example_en': 'Develop the product iteratively', 'example_ru': 'Разрабатывайте продукт итеративно'},
    {'en': 'medium', 'ru': 'средство, метод общения', 'example_en': 'Choose the right medium for communication', 'example_ru': 'Выберите правильное средство для общения'},
    {'en': 'memorability', 'ru': 'запоминаемость', 'example_en': 'Improve the memorability of the interface', 'example_ru': 'Улучшите запоминаемость интерфейса'},
    {'en': 'musculoskeletal disorder', 'ru': 'расстройство опорно-двигательного аппарата', 'example_en': 'Prevent musculoskeletal disorders with ergonomic design', 'example_ru': 'Предотвращайте расстройства опорно-двигательного аппарата эргономичным дизайном'},
    {'en': 'objective', 'ru': 'цель; что-то, что планируете достичь', 'example_en': 'Define clear objectives for the project', 'example_ru': 'Определите четкие цели для проекта'},
    {'en': 'pave the way', 'ru': 'проложить путь', 'example_en': 'This innovation will pave the way for future developments', 'example_ru': 'Эта инновация проложит путь для будущих разработок'},
    {'en': 'posture', 'ru': 'поза, положение', 'example_en': 'Maintain good posture while coding', 'example_ru': 'Поддерживайте хорошую осанку во время программирования'},
    {'en': 'refine', 'ru': 'совершенствовать, улучшать', 'example_en': 'Refine the algorithm for better performance', 'example_ru': 'Усовершенствуйте алгоритм для лучшей производительности'},
    {'en': 'retain', 'ru': 'сохранять, удерживать', 'example_en': 'Retain user data securely', 'example_ru': 'Безопасно сохраняйте пользовательские данные'},
    {'en': 'strain', 'ru': 'напряжение, нагрузка', 'example_en': 'Reduce eye strain with proper lighting', 'example_ru': 'Снизьте напряжение глаз правильным освещением'},
    {'en': 'streamline', 'ru': 'оптимизировать', 'example_en': 'Streamline the development process', 'example_ru': 'Оптимизируйте процесс разработки'},
    {'en': 'survey', 'ru': 'опрос', 'example_en': 'Conduct a user survey for feedback', 'example_ru': 'Проведите опрос пользователей для получения обратной связи'},
    {'en': 'various', 'ru': 'разный, различный', 'example_en': 'Test on various devices and browsers', 'example_ru': 'Тестируйте на различных устройствах и браузерах'},
    {'en': 'vehicle', 'ru': 'транспортное средство', 'example_en': 'Software is the vehicle for digital transformation', 'example_ru': 'ПО - это средство цифровой трансформации'},
    {'en': 'abandonment', 'ru': 'отказ, оставление', 'example_en': 'High cart abandonment rate indicates UX issues', 'example_ru': 'Высокий показатель отказа от корзины указывает на проблемы UX'},
    {'en': 'artery', 'ru': 'артерия', 'example_en': 'The main network artery handles most traffic', 'example_ru': 'Главная сетевая артерия обрабатывает большую часть трафика'},
    {'en': 'behemoth', 'ru': 'гигант, бегемот', 'example_en': 'Google is a tech behemoth', 'example_ru': 'Google - это технологический гигант'},
    {'en': 'benchmark', 'ru': 'эталон, отметка высоты', 'example_en': 'Set performance benchmarks for the system', 'example_ru': 'Установите эталоны производительности для системы'},
    {'en': 'biennially', 'ru': 'каждые два года', 'example_en': 'The conference is held biennially', 'example_ru': 'Конференция проводится каждые два года'},
    {'en': 'bolster', 'ru': 'поддерживать', 'example_en': 'Bolster security with additional measures', 'example_ru': 'Укрепите безопасность дополнительными мерами'},
    {'en': 'consecutive', 'ru': 'последовательный', 'example_en': 'The system failed three consecutive times', 'example_ru': 'Система сбоила три раза подряд'},
    {'en': 'deter', 'ru': 'сдерживать, удерживать', 'example_en': 'Strong encryption deters hackers', 'example_ru': 'Сильное шифрование сдерживает хакеров'},
    {'en': 'enticing', 'ru': 'заманчивый, соблазнительный', 'example_en': 'The new features are enticing to users', 'example_ru': 'Новые функции заманчивы для пользователей'},
    {'en': 'excel in', 'ru': 'преуспеть в', 'example_en': 'Our team excels in mobile development', 'example_ru': 'Наша команда преуспевает в мобильной разработке'},
    {'en': 'exponentially', 'ru': 'показательно', 'example_en': 'Data growth is increasing exponentially', 'example_ru': 'Рост данных увеличивается экспоненциально'},
    {'en': 'frontrunner', 'ru': 'лидер', 'example_en': 'Python is the frontrunner for AI development', 'example_ru': 'Python - лидер в разработке ИИ'},
    {'en': 'governance', 'ru': 'управление, руководство', 'example_en': 'Establish proper data governance', 'example_ru': 'Установите надлежащее управление данными'},
    {'en': 'hit the market', 'ru': 'выйти на рынок', 'example_en': 'The product will hit the market next month', 'example_ru': 'Продукт выйдет на рынок в следующем месяце'},
    {'en': 'holistic', 'ru': 'целостный', 'example_en': 'Take a holistic approach to system design', 'example_ru': 'Применяйте целостный подход к проектированию системы'},
    {'en': 'incentive', 'ru': 'стимул, побуждение', 'example_en': 'Provide incentives for code quality', 'example_ru': 'Предоставьте стимулы для качества кода'},
    {'en': 'incentivization', 'ru': 'стимулирование', 'example_en': 'User incentivization improves engagement', 'example_ru': 'Стимулирование пользователей улучшает вовлеченность'},
    {'en': 'lag', 'ru': 'отставать', 'example_en': 'Don\'t let your skills lag behind technology', 'example_ru': 'Не позволяйте своим навыкам отставать от технологий'},
    {'en': 'literacy', 'ru': 'грамотность', 'example_en': 'Improve digital literacy in the organization', 'example_ru': 'Повышайте цифровую грамотность в организации'},
    {'en': 'monetary transactions', 'ru': 'денежные операции', 'example_en': 'Secure all monetary transactions', 'example_ru': 'Обезопасьте все денежные операции'},
    {'en': 'poise', 'ru': 'уравновешивать, балансировать', 'example_en': 'The system is poised for major updates', 'example_ru': 'Система готова к крупным обновлениям'},
    {'en': 'proliferation', 'ru': 'распространение', 'example_en': 'The proliferation of mobile devices changes everything', 'example_ru': 'Распространение мобильных устройств меняет все'},
    {'en': 'reaffirm position', 'ru': 'подтвердить позицию', 'example_en': 'The company reaffirmed its position on privacy', 'example_ru': 'Компания подтвердила свою позицию по конфиденциальности'},
    {'en': 'replicate', 'ru': 'повторять, копировать', 'example_en': 'Replicate the database for backup', 'example_ru': 'Реплицируйте базу данных для резервного копирования'},
    {'en': 'rival', 'ru': 'соперник, конкурент', 'example_en': 'Our main rival released a similar product', 'example_ru': 'Наш главный конкурент выпустил похожий продукт'},
    {'en': 'rural', 'ru': 'деревенский, сельский', 'example_en': 'Improve internet access in rural areas', 'example_ru': 'Улучшите доступ к интернету в сельских районах'},
    {'en': 'saddle with', 'ru': 'взваливать (на кого-л.) что-л.', 'example_en': 'Don\'t saddle the team with unrealistic deadlines', 'example_ru': 'Не взваливайте на команду нереалистичные сроки'},
    {'en': 'seamlessly', 'ru': 'бесшовно', 'example_en': 'The systems integrate seamlessly', 'example_ru': 'Системы интегрируются бесшовно'},
    {'en': 'shipping', 'ru': 'перевозка груза, доставка', 'example_en': 'We\'re shipping the new version tomorrow', 'example_ru': 'Мы выпускаем новую версию завтра'},
    {'en': 'shopping cart', 'ru': 'корзина', 'example_en': 'Add items to your shopping cart', 'example_ru': 'Добавьте товары в корзину'},
    {'en': 'solely', 'ru': 'исключительно, только', 'example_en': 'The decision was based solely on performance', 'example_ru': 'Решение основывалось исключительно на производительности'},
    {'en': 'stride', 'ru': 'шаг, большой шаг', 'example_en': 'Make great strides in development', 'example_ru': 'Делайте большие шаги в разработке'},
    {'en': 'table', 'ru': 'планшет', 'example_en': 'The data is displayed in a table format', 'example_ru': 'Данные отображаются в табличном формате'},
    {'en': 'tailor', 'ru': 'адаптировать, специально приспосабливать', 'example_en': 'Tailor the solution to client needs', 'example_ru': 'Адаптируйте решение под потребности клиента'},
    {'en': 'thread', 'ru': 'нить', 'example_en': 'The execution thread handles multiple tasks', 'example_ru': 'Поток выполнения обрабатывает несколько задач'},
    {'en': 'upswing', 'ru': 'подъем, рост', 'example_en': 'The market is on an upswing', 'example_ru': 'Рынок находится на подъеме'},
    {'en': 'weave', 'ru': 'плести, вплетать', 'example_en': 'Weave security into the application design', 'example_ru': 'Вплетите безопасность в дизайн приложения'},
    {'en': 'advent', 'ru': 'появление, пришествие', 'example_en': 'The advent of AI changed everything', 'example_ru': 'Появление ИИ изменило все'},
    {'en': 'ambient', 'ru': 'окружающий, внешний', 'example_en': 'Monitor ambient temperature in the server room', 'example_ru': 'Контролируйте температуру окружающей среды в серверной'},
    {'en': 'appropriate', 'ru': 'присваивать', 'example_en': 'Don\'t appropriate code without permission', 'example_ru': 'Не присваивайте код без разрешения'},
    {'en': 'bear false witness', 'ru': 'давать ложные показания; лжесвидетельствовать', 'example_en': 'Never bear false witness in code reviews', 'example_ru': 'Никогда не лжесвидетельствуйте при обзоре кода'},
    {'en': 'by any stretch', 'ru': 'как ни напрягай фантазию, при всём желании', 'example_en': 'This code is not optimal by any stretch', 'example_ru': 'Этот код при всем желании не оптимален'},
    {'en': 'clear-cut', 'ru': 'чёткий, ясный, отчётливый', 'example_en': 'We need clear-cut requirements', 'example_ru': 'Нам нужны четкие требования'},
    {'en': 'commandment', 'ru': 'заповедь, наказ, предписание', 'example_en': 'Follow the coding commandments', 'example_ru': 'Следуйте заповедям программирования'},
    {'en': 'consideration', 'ru': 'уважение, предупредительность', 'example_en': 'Show consideration for user privacy', 'example_ru': 'Проявляйте уважение к конфиденциальности пользователей'},
    {'en': 'constitute a theft', 'ru': 'квалифицироваться как кража; является кражей', 'example_en': 'Copying code may constitute a theft', 'example_ru': 'Копирование кода может квалифицироваться как кража'},
    {'en': 'contested', 'ru': 'спорный, оспариваемый', 'example_en': 'The patent is heavily contested', 'example_ru': 'Патент активно оспаривается'},
    {'en': 'eliminate bias', 'ru': 'устранить предвзятость', 'example_en': 'We must eliminate bias from our algorithms', 'example_ru': 'Мы должны устранить предвзятость из наших алгоритмов'},
    {'en': 'enforcement', 'ru': 'соблюдение, исполнение', 'example_en': 'Security policy enforcement is critical', 'example_ru': 'Соблюдение политики безопасности критически важно'},
    {'en': 'fraud', 'ru': 'обман, мошенничество, подделка', 'example_en': 'Detect fraud in financial transactions', 'example_ru': 'Обнаруживайте мошенничество в финансовых операциях'},
    {'en': 'impartiality', 'ru': 'беспристрастность, объективность', 'example_en': 'Maintain impartiality in code reviews', 'example_ru': 'Сохраняйте беспристрастность при обзоре кода'},
    {'en': 'insure', 'ru': 'обеспечить', 'example_en': 'Insure data integrity with checksums', 'example_ru': 'Обеспечьте целостность данных с помощью контрольных сумм'},
    {'en': 'justifiable', 'ru': 'оправданный, правомерный, законный, допустимый', 'example_en': 'The performance trade-off is justifiable', 'example_ru': 'Компромисс в производительности оправдан'},
    {'en': 'opaque', 'ru': 'непрозрачный, непроницаемый', 'example_en': 'The API design is too opaque', 'example_ru': 'Дизайн API слишком непрозрачен'},
    {'en': 'overlap', 'ru': 'совпадать, пересекаться', 'example_en': 'These functions overlap in functionality', 'example_ru': 'Эти функции пересекаются по функциональности'},
    {'en': 'pertinent', 'ru': 'соответствующий, уместный', 'example_en': 'Include only pertinent information', 'example_ru': 'Включайте только соответствующую информацию'},
    {'en': 'pervasive', 'ru': 'всепроникающий, повсеместно распространенный', 'example_en': 'Mobile technology is pervasive', 'example_ru': 'Мобильные технологии повсеместно распространены'},
    {'en': 'prey', 'ru': 'обманывать, наживаться, грабить', 'example_en': 'Scammers prey on vulnerable users', 'example_ru': 'Мошенники наживаются на уязвимых пользователях'},
    {'en': 'proprietary', 'ru': 'запатентованный, частный, личный, чужой', 'example_en': 'This is proprietary software', 'example_ru': 'Это проприетарное программное обеспечение'},
    {'en': 'repercussion', 'ru': 'последствия, отголосок, отзвук', 'example_en': 'Consider the repercussions of this change', 'example_ru': 'Рассмотрите последствия этого изменения'},
    {'en': 'scam', 'ru': 'афера, мошенничество', 'example_en': 'Protect users from online scams', 'example_ru': 'Защищайте пользователей от онлайн-мошенничества'},
    {'en': 'snoop around', 'ru': 'вынюхивать, выслеживать, шпионить', 'example_en': 'Don\'t let malware snoop around your system', 'example_ru': 'Не позволяйте вредоносному ПО шпионить в вашей системе'},
    {'en': 'strive', 'ru': 'стараться, стремиться', 'example_en': 'Strive for code excellence', 'example_ru': 'Стремитесь к совершенству кода'},
    {'en': 'tenet', 'ru': 'принцип, постулат', 'example_en': 'Follow the basic tenets of software design', 'example_ru': 'Следуйте основным принципам разработки ПО'},
    {'en': 'ubiquitous', 'ru': 'вездесущий, повсеместный', 'example_en': 'Smartphones are ubiquitous today', 'example_ru': 'Смартфоны сегодня повсеместны'},
    {'en': 'assembly-line', 'ru': 'сборочная линия', 'example_en': 'Automate the software assembly-line', 'example_ru': 'Автоматизируйте сборочную линию программного обеспечения'},
    {'en': 'bank teller', 'ru': 'кассир банка', 'example_en': 'The ATM replaced many bank tellers', 'example_ru': 'Банкомат заменил многих банковских кассиров'},
    {'en': 'bartender', 'ru': 'бармен', 'example_en': 'AI bartender serves digital cocktails', 'example_ru': 'ИИ-бармен подает цифровые коктейли'},
    {'en': 'bowling pinsetter', 'ru': 'установщик кеглей для боулинга', 'example_en': 'Automated bowling pinsetter improves efficiency', 'example_ru': 'Автоматизированный установщик кеглей повышает эффективность'},
    {'en': 'comb through', 'ru': 'просматривать', 'example_en': 'Comb through the logs for errors', 'example_ru': 'Просмотрите логи на предмет ошибок'},
    {'en': 'commonplace', 'ru': 'обычное дело/явление', 'example_en': 'Cloud computing is commonplace now', 'example_ru': 'Облачные вычисления теперь обычное дело'},
    {'en': 'construction', 'ru': 'строительство', 'example_en': 'Software construction requires planning', 'example_ru': 'Создание программного обеспечения требует планирования'},
    {'en': 'dozing', 'ru': 'работа бульдозером', 'example_en': 'Data dozing clears old records', 'example_ru': 'Расчистка данных удаляет старые записи'},
    {'en': 'draft', 'ru': 'составлять; набрасывать черновик', 'example_en': 'Draft the technical specification first', 'example_ru': 'Сначала составьте техническую спецификацию'},
    {'en': 'drive-thru', 'ru': 'автокафе, обслуживание не выходя из машины', 'example_en': 'API acts like a drive-thru service', 'example_ru': 'API работает как сервис без выхода из машины'},
    {'en': 'endanger', 'ru': 'подвергать опасности', 'example_en': 'Poor security practices endanger users', 'example_ru': 'Плохие практики безопасности подвергают пользователей опасности'},
    {'en': 'film projectionist', 'ru': 'киномеханик', 'example_en': 'Digital systems replaced film projectionists', 'example_ru': 'Цифровые системы заменили киномехаников'},
    {'en': 'forklift machine', 'ru': 'вилочный погрузчик, грузоподъемник', 'example_en': 'Automated forklift machines work in warehouses', 'example_ru': 'Автоматизированные погрузчики работают на складах'},
    {'en': 'grocery store', 'ru': 'продуктовый магазин', 'example_en': 'Online grocery stores are growing', 'example_ru': 'Онлайн продуктовые магазины растут'},
    {'en': 'hauling', 'ru': 'транспортировка, перевозка', 'example_en': 'Data hauling requires high bandwidth', 'example_ru': 'Транспортировка данных требует высокой пропускной способности'},
    {'en': 'infantry', 'ru': 'пехота', 'example_en': 'Junior developers are the infantry of coding', 'example_ru': 'Младшие разработчики - это пехота программирования'},
    {'en': 'jack', 'ru': 'гнездо', 'example_en': 'Plug the cable into the network jack', 'example_ru': 'Подключите кабель к сетевому гнезду'},
    {'en': 'lawnmower', 'ru': 'газонокосилка', 'example_en': 'Robotic lawnmowers use GPS navigation', 'example_ru': 'Роботизированные газонокосилки используют GPS-навигацию'},
    {'en': 'mining', 'ru': 'горнодобывающая промышленность', 'example_en': 'Data mining extracts valuable insights', 'example_ru': 'Добыча данных извлекает ценную информацию'},
    {'en': 'paralegal', 'ru': 'помощник юриста', 'example_en': 'AI can assist paralegals with research', 'example_ru': 'ИИ может помочь помощникам юристов с исследованиями'},
    {'en': 'reel', 'ru': 'катушка', 'example_en': 'The tape reel stores backup data', 'example_ru': 'Катушка с лентой хранит резервные данные'},
    {'en': 'shipment of goods', 'ru': 'доставка товаров', 'example_en': 'Track shipment of goods with RFID', 'example_ru': 'Отслеживайте доставку товаров с помощью RFID'},
    {'en': 'stagger', 'ru': 'ошеломлять, потрясать, поражать', 'example_en': 'The performance improvements stagger users', 'example_ru': 'Улучшения производительности поражают пользователей'},
    {'en': 'stockroom', 'ru': 'складское помещение, хранилище', 'example_en': 'Digital stockroom manages inventory', 'example_ru': 'Цифровое хранилище управляет запасами'},
    {'en': 'switchboard operator', 'ru': 'оператор коммутатора', 'example_en': 'Automated systems replaced switchboard operators', 'example_ru': 'Автоматизированные системы заменили операторов коммутатора'},
    {'en': 'troubleshooting', 'ru': 'аварийный, поиск неисправностей', 'example_en': 'Troubleshooting skills are essential', 'example_ru': 'Навыки поиска неисправностей необходимы'},
    {'en': 'typist', 'ru': 'машинистка', 'example_en': 'Voice recognition replaced many typists', 'example_ru': 'Распознавание голоса заменило многих машинисток'},
    {'en': 'warehousing', 'ru': 'складирование', 'example_en': 'Data warehousing stores historical information', 'example_ru': 'Складирование данных хранит историческую информацию'},
    {'en': 'weeds', 'ru': 'сорняки, бурьян', 'example_en': 'Remove code weeds during refactoring', 'example_ru': 'Удаляйте сорняки кода во время рефакторинга'},
    {'en': 'withdraw', 'ru': 'изымать, забирать, брать назад', 'example_en': 'Withdraw the deprecated feature', 'example_ru': 'Изымите устаревшую функцию'},
    {'en': 'obsolete', 'ru': 'устаревший, отживший', 'example_en': 'This technology is obsolete', 'example_ru': 'Эта технология устарела'}
]

# Файл для сохранения данных пользователей
USER_DATA_FILE = 'users.json'

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

def init_user(user_id, user_name):
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user_name,
            'learned_terms': [],
            'quiz_stats': {
                'correct': 0,
                'total': 0,
                'streak': 0,
                'best_streak': 0
            },
            'score': 0,
            'join_date': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        save_user_data(user_data)
else:
        # ← ДОБАВИТЬ ЭТИ 2 СТРОКИ
        user_data[user_id]['last_activity'] = datetime.now().isoformat()
        save_user_data(user_data)
    return user_data[user_id]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # Инициализация пользователя
    user_profile = init_user(user_id, user.first_name)
    
    keyboard = [
        [InlineKeyboardButton("📚 Изучать термины", callback_data="learn")],
        [InlineKeyboardButton("🧠 Викторина", callback_data="quiz")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    learned_count = len(user_profile['learned_terms'])
    total_count = len(TERMS_DATABASE)
    accuracy = round(user_profile['quiz_stats']['correct']/max(user_profile['quiz_stats']['total'], 1)*100)
    
    welcome_text = f"""🚀 <b>English Terms Bot</b>

Привет, {user.first_name}! 👋

📈 <b>Твой прогресс:</b>
📚 Изучено: {learned_count}/{total_count} терминов
⭐ Очки: {user_profile['score']}
🎯 Точность: {accuracy}%
🔥 Лучшая серия: {user_profile['quiz_stats']['best_streak']}

Выбери действие:"""
    
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    if query.data == "learn":
        await show_term(query, user_id)
    elif query.data == "quiz":
        await start_quiz(query, user_id, context)
    elif query.data == "stats":
        await show_statistics(query, user_id)
    elif query.data == "help":
        await show_help(query)
    elif query.data == "next_term":
        await show_term(query, user_id)
    elif query.data == "back_main":
        await back_to_main(query, user_id)
    elif query.data.startswith("answer_"):
        await handle_quiz_answer(query, user_id, context)

async def show_term(query, user_id):
    user_profile = user_data[user_id]
    
    # Выбираем случайный термин
    term = random.choice(TERMS_DATABASE)
    
    # Проверяем, новый ли это термин
    is_new = term['en'] not in user_profile['learned_terms']
    
    if is_new:
        user_profile['learned_terms'].append(term['en'])
        user_profile['score'] += 5
        save_user_data(user_data)
    
    new_badge = " 🆕" if is_new else ""
    points_text = f"\n\n🎉 <b>+5 очков за новый термин!</b>" if is_new else ""
    
    text = f"""📚 <b>Изучение терминов{new_badge}</b>

🇬🇧 <b>English:</b> {term['en']}
🇷🇺 <b>Русский:</b> {term['ru']}

📝 <b>Примеры:</b>
🇬🇧 {term['example_en']}
🇷🇺 {term['example_ru']}

💡 <i>Запомни этот термин!</i>{points_text}"""
    
    keyboard = [
        [InlineKeyboardButton("➡️ Следующий термин", callback_data="next_term")],
        [InlineKeyboardButton("🧠 Викторина", callback_data="quiz")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def start_quiz(query, user_id, context):
    user_profile = user_data[user_id]
    
    if len(user_profile['learned_terms']) < 4:
        text = """❌ <b>Недостаточно изученных терминов!</b>

Для викторины нужно изучить минимум 4 термина.

📚 Начни с изучения терминов!"""
        
        keyboard = [[InlineKeyboardButton("📚 Изучать термины", callback_data="learn")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
        return
    
    # Выбираем случайный изученный термин
    learned_terms = [term for term in TERMS_DATABASE if term['en'] in user_profile['learned_terms']]
    quiz_term = random.choice(learned_terms)
    
    # Создаем варианты ответов
    all_terms = TERMS_DATABASE.copy()
    wrong_answers = [term['ru'] for term in all_terms if term['en'] != quiz_term['en']]
    random.shuffle(wrong_answers)
    
    # Берем 3 неправильных ответа
    options = [quiz_term['ru']] + wrong_answers[:3]
    random.shuffle(options)
    
    correct_index = options.index(quiz_term['ru'])
    
    # Сохраняем данные викторины
    context.user_data[f'quiz_correct_{user_id}'] = correct_index
    context.user_data[f'quiz_term_{user_id}'] = quiz_term['en']
    context.user_data[f'quiz_answer_{user_id}'] = quiz_term['ru']
    
    text = f"""🧠 <b>Викторина</b>

Как переводится термин:
<b>"{quiz_term['en']}"</b>

🎯 Выбери правильный ответ:"""
    
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"answer_{i}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def handle_quiz_answer(query, user_id, context):
    selected = int(query.data.split("_")[1])
    
    # Получаем сохраненные данные викторины
    correct_index = context.user_data.get(f'quiz_correct_{user_id}', 0)
    quiz_term = context.user_data.get(f'quiz_term_{user_id}', '')
    correct_answer = context.user_data.get(f'quiz_answer_{user_id}', '')
    
    user_profile = user_data[user_id]
    user_profile['quiz_stats']['total'] += 1
    
    is_correct = selected == correct_index
    
    if is_correct:
        user_profile['quiz_stats']['correct'] += 1
        user_profile['quiz_stats']['streak'] += 1
        user_profile['score'] += 10
        
        # Обновляем лучшую серию
        if user_profile['quiz_stats']['streak'] > user_profile['quiz_stats']['best_streak']:
            user_profile['quiz_stats']['best_streak'] = user_profile['quiz_stats']['streak']
        
        text = f"""✅ <b>Правильно!</b>

🎉 Отлично! <b>"{quiz_term}" = "{correct_answer}"</b>
⭐ <b>+10 очков!</b>
🔥 Серия правильных ответов: {user_profile['quiz_stats']['streak']}

📊 Твой счет: {user_profile['score']} очков
🎯 Точность: {user_profile['quiz_stats']['correct']}/{user_profile['quiz_stats']['total']} ({round(user_profile['quiz_stats']['correct']/user_profile['quiz_stats']['total']*100)}%)"""
    else:
        user_profile['quiz_stats']['streak'] = 0  # Сбрасываем серию
        
        text = f"""❌ <b>Неправильно!</b>

💡 Правильный ответ: <b>"{quiz_term}" = "{correct_answer}"</b>
😊 Не расстраивайся, продолжай учиться!

📊 Твой счет: {user_profile['score']} очков  
🎯 Точность: {user_profile['quiz_stats']['correct']}/{user_profile['quiz_stats']['total']} ({round(user_profile['quiz_stats']['correct']/user_profile['quiz_stats']['total']*100)}%)"""
    
    save_user_data(user_data)
    
    keyboard = [
        [InlineKeyboardButton("🧠 Следующий вопрос", callback_data="quiz")],
        [InlineKeyboardButton("📚 Изучать термины", callback_data="learn")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_statistics(query, user_id):
    user_profile = user_data[user_id]
    
    learned_count = len(user_profile['learned_terms'])
    total_count = len(TERMS_DATABASE)
    progress_percentage = round(learned_count / total_count * 100)
    accuracy = round(user_profile['quiz_stats']['correct']/max(user_profile['quiz_stats']['total'], 1)*100)
    
    # Определяем уровень
    if learned_count >= 25:
        level = "🏆 Эксперт"
    elif learned_count >= 15:
        level = "🥈 Продвинутый"
    elif learned_count >= 8:
        level = "🥉 Изучающий"
    else:
        level = "🌱 Новичок"
    
    text = f"""📊 <b>Статистика {user_profile['name']}</b>

{level}
📚 <b>Изучено терминов:</b> {learned_count}/{total_count} ({progress_percentage}%)
⭐ <b>Набрано очков:</b> {user_profile['score']}
🧠 <b>Тестов пройдено:</b> {user_profile['quiz_stats']['total']}
🎯 <b>Точность ответов:</b> {accuracy}%
🔥 <b>Лучшая серия:</b> {user_profile['quiz_stats']['best_streak']}

📅 <i>Присоединился: {user_profile['join_date'][:10]}</i>"""
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_help(query):
    text = """ℹ️ <b>Помощь - English Terms Bot</b>

🎯 <b>Возможности бота:</b>

📚 <b>Изучение терминов</b>
• 30 популярных IT терминов
• Примеры на английском и русском
• +5 очков за каждый новый термин

🧠 <b>Викторина</b>
• Тесты по изученным терминам
• +10 очков за правильный ответ
• Система серий правильных ответов

📊 <b>Статистика</b>
• Отслеживание прогресса
• Система очков и уровней
• Статистика точности ответов

🏆 <b>Система уровней:</b>
🌱 Новичок: 0-7 терминов
🥉 Изучающий: 8-14 терминов
🥈 Продвинутый: 15-24 термина
🏆 Эксперт: 25+ терминов

💡 <i>Начни с изучения терминов, затем проверь знания в викторине!</i>"""
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def back_to_main(query, user_id):
    user = query.from_user
    user_profile = user_data[user_id]
    
    keyboard = [
        [InlineKeyboardButton("📚 Изучать термины", callback_data="learn")],
        [InlineKeyboardButton("🧠 Викторина", callback_data="quiz")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    learned_count = len(user_profile['learned_terms'])
    total_count = len(TERMS_DATABASE)
    accuracy = round(user_profile['quiz_stats']['correct']/max(user_profile['quiz_stats']['total'], 1)*100)
    
    welcome_text = f"""🚀 <b>English Terms Bot</b>

Привет, {user.first_name}! 👋

📈 <b>Твой прогресс:</b>
📚 Изучено: {learned_count}/{total_count} терминов
⭐ Очки: {user_profile['score']}
🎯 Точность: {accuracy}%

Выбери действие:"""
    
    await query.edit_message_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ панель - только для администратора"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет доступа к админ панели.")
        return
    
    total_users = len(user_data)
    
    # Статистика активности
    today = datetime.now().date()
    active_today = 0
    total_queries = 0
    total_learned = 0
    
    for user_profile in user_data.values():
        total_queries += user_profile['quiz_stats']['total']
        total_learned += len(user_profile['learned_terms'])
        
        try:
            last_activity = datetime.fromisoformat(user_profile['last_activity']).date()
            if last_activity == today:
                active_today += 1
        except:
            pass
    
    # Топ-3 активных пользователя
    sorted_users = sorted(
        user_data.items(), 
        key=lambda x: x[1]['score'], 
        reverse=True
    )[:3]
    
    top_users_text = ""
    for i, (user_id, profile) in enumerate(sorted_users, 1):
        top_users_text += f"{i}. {profile['name']} - {profile['score']} очков\n"
    
    admin_text = f"""🔧 **АДМИН ПАНЕЛЬ**

📊 **Общая статистика:**
👥 Всего пользователей: {total_users}
🟢 Активных сегодня: {active_today}
📝 Всего тестов пройдено: {total_queries}
📚 Всего терминов изучено: {total_learned}
📖 Терминов в базе: {len(TERMS_DATABASE)}

🏆 **Топ-3 пользователя:**
{top_users_text if top_users_text else "Пока нет данных"}

⏰ Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    await update.message.reply_text(admin_text, parse_mode='Markdown')

def main():
    print('🚀 Запуск English Terms Bot...')
    print('📚 База данных: 30 терминов')
    print('🧠 Викторина с примерами')
    print('📊 Система статистики')
    
    if not TOKEN:
        print('❌ BOT_TOKEN не найден!')
        return
    
    try:
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CommandHandler('start', start_command))
        application.add_handler(CommandHandler('admin', admin_panel)) 
        application.add_handler(CallbackQueryHandler(button_handler))
        
        print('✅ English Terms Bot запущен!')
        print('=' * 50)
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f'❌ Критическая ошибка: {e}')
        logger.error(f'Critical error: {e}')

if __name__ == '__main__':
    main()
