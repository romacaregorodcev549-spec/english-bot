import os
import json
import random
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = '8609800555:AAGO33Tub9bYSxskT92HWGvYdASaFWzW5Gs'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# Состояние пользователей
user_state = {}
user_last_text = {}
user_levels = {}
user_test = {}
user_points = {}
user_streak = {}
user_achievements = {}
user_review_cards = {}

# Система уровней
LEVEL_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1']
LEVEL_TESTS = {}
LEVEL_PASSED = {}

# ===== БАЗА ЗНАНИЙ =====
WORDS = {
    'A1': {
        'words': [
            ('apple','яблоко','Еда'),('banana','банан','Еда'),('bread','хлеб','Еда'),
            ('water','вода','Еда'),('milk','молоко','Еда'),('egg','яйцо','Еда'),
            ('fish','рыба','Еда'),('meat','мясо','Еда'),('rice','рис','Еда'),
            ('soup','суп','Еда'),('cake','торт','Еда'),('juice','сок','Еда'),
            ('tea','чай','Еда'),('coffee','кофе','Еда'),('sugar','сахар','Еда'),
            ('salt','соль','Еда'),('cheese','сыр','Еда'),('butter','масло','Еда'),
            ('chicken','курица','Еда'),('salad','салат','Еда'),('pizza','пицца','Еда'),
            ('cat','кот','Животные'),('dog','собака','Животные'),('bird','птица','Животные'),
            ('horse','лошадь','Животные'),('cow','корова','Животные'),('pig','свинья','Животные'),
            ('house','дом','Дом'),('room','комната','Дом'),('door','дверь','Дом'),
            ('window','окно','Дом'),('table','стол','Дом'),('chair','стул','Дом'),
            ('bed','кровать','Дом'),('kitchen','кухня','Дом'),('bathroom','ванная','Дом'),
            ('shirt','рубашка','Одежда'),('dress','платье','Одежда'),('shoes','обувь','Одежда'),
            ('red','красный','Цвета'),('blue','синий','Цвета'),('green','зелёный','Цвета'),
            ('yellow','жёлтый','Цвета'),('white','белый','Цвета'),('black','чёрный','Цвета'),
            ('big','большой','Прил'),('small','маленький','Прил'),('good','хороший','Прил'),
            ('bad','плохой','Прил'),('new','новый','Прил'),('old','старый','Прил'),
            ('hot','горячий','Прил'),('cold','холодный','Прил'),('happy','счастливый','Прил'),
            ('sad','грустный','Прил'),('hungry','голодный','Прил'),('tired','уставший','Прил'),
            ('friend','друг','Люди'),('family','семья','Люди'),('mother','мама','Люди'),
            ('father','папа','Люди'),('brother','брат','Люди'),('sister','сестра','Люди'),
            ('time','время','Время'),('day','день','Время'),('night','ночь','Время'),
            ('morning','утро','Время'),('week','неделя','Время'),('year','год','Время'),
            ('sun','солнце','Природа'),('moon','луна','Природа'),('star','звезда','Природа'),
            ('tree','дерево','Природа'),('flower','цветок','Природа'),('rain','дождь','Природа'),
            ('car','машина','Транспорт'),('bus','автобус','Транспорт'),('train','поезд','Транспорт'),
            ('go','идти','Глаголы'),('come','приходить','Глаголы'),('eat','есть','Глаголы'),
            ('drink','пить','Глаголы'),('sleep','спать','Глаголы'),('see','видеть','Глаголы'),
            ('hear','слышать','Глаголы'),('speak','говорить','Глаголы'),('read','читать','Глаголы'),
            ('write','писать','Глаголы'),('like','нравиться','Глаголы'),('love','любить','Глаголы'),
        ],
        'phrases': [
            ('Hello','Привет'),('Good morning','Доброе утро'),('Good night','Спокойной ночи'),
            ('How are you?','Как дела?'),('Thank you','Спасибо'),('Please','Пожалуйста'),
            ('My name is...','Меня зовут...'),('Nice to meet you','Приятно познакомиться'),
            ('I like it','Мне нравится'),('I don\'t know','Я не знаю'),
            ('Where is...?','Где...?'),('How much?','Сколько?'),
        ],
        'texts': [
            ('My Day','I wake up at 7. I eat breakfast. I go to work. I come home at 6. I watch TV. I go to bed at 11.','Я просыпаюсь в 7. Я завтракаю. Я иду на работу. Я прихожу домой в 6. Я смотрю ТВ. Я ложусь спать в 11.'),
        ],
        'pics': ['https://picsum.photos/400/300?1','https://picsum.photos/400/300?2','https://picsum.photos/400/300?3']
    },
    'A2': {
        'words': [
            ('market','рынок','Еда'),('vegetable','овощ','Еда'),('fruit','фрукт','Еда'),
            ('weather','погода','Природа'),('snow','снег','Природа'),('river','река','Природа'),
            ('mountain','гора','Природа'),('hospital','больница','Город'),('shop','магазин','Город'),
            ('clothes','одежда','Одежда'),('music','музыка','Развл'),('sport','спорт','Развл'),
            ('work','работа','Работа'),('money','деньги','Работа'),('cheap','дешёвый','Прил'),
            ('expensive','дорогой','Прил'),('easy','лёгкий','Прил'),('difficult','сложный','Прил'),
            ('interesting','интересный','Прил'),('boring','скучный','Прил'),
            ('think','думать','Глаголы'),('believe','верить','Глаголы'),('try','пытаться','Глаголы'),
            ('change','менять','Глаголы'),('remember','помнить','Глаголы'),('forget','забывать','Глаголы'),
        ],
        'phrases': [
            ('What time is it?','Который час?'),('I would like...','Я бы хотел...'),
            ('Can you help?','Можете помочь?'),('I don\'t understand','Я не понимаю'),
            ('in my opinion','по моему мнению'),('for example','например'),
        ],
        'texts': [
            ('Weekend','Last weekend I went to the park. The weather was sunny. We played football. It was great!','На прошлых выходных я ходил в парк. Погода была солнечная. Мы играли в футбол. Было здорово!'),
        ],
        'pics': ['https://picsum.photos/400/300?4','https://picsum.photos/400/300?5','https://picsum.photos/400/300?6']
    },
    'B1': {
        'words': [
            ('achievement','достижение'),('advantage','преимущество'),('advice','совет'),
            ('behaviour','поведение'),('challenge','вызов'),('choice','выбор'),
            ('communication','общение'),('culture','культура'),('decision','решение'),
            ('education','образование'),('environment','окружающая среда'),
            ('experience','опыт'),('freedom','свобода'),('knowledge','знание'),
            ('opportunity','возможность'),('patience','терпение'),('success','успех'),
        ],
        'phrases': [
            ('As a result','В результате'),('In addition','Кроме того'),
            ('On the contrary','Наоборот'),('In conclusion','В заключение'),
            ('To be honest','Честно говоря'),('In other words','Другими словами'),
        ],
        'texts': [
            ('Technology','Technology has changed our lives. People use smartphones for work and entertainment. However, too much screen time can be harmful.','Технологии изменили нашу жизнь. Люди используют смартфоны для работы и развлечений. Однако слишком много времени перед экраном может быть вредно.'),
        ],
        'pics': ['https://picsum.photos/400/300?7','https://picsum.photos/400/300?8']
    },
    'B2': {
        'words': [
            ('abundant','обильный'),('accurate','точный'),('appropriate','подходящий'),
            ('comprehensive','всесторонний'),('crucial','решающий'),('diverse','разнообразный'),
            ('efficient','эффективный'),('evidence','доказательство'),
            ('fundamental','фундаментальный'),('implement','осуществлять'),
            ('inevitable','неизбежный'),('maintain','поддерживать'),
            ('outcome','исход'),('significant','значительный'),('sufficient','достаточный'),
        ],
        'phrases': [
            ('As a matter of fact','На самом деле'),('In the long run','В долгосрочной перспективе'),
            ('On the whole','В целом'),('Without a doubt','Без сомнения'),
        ],
        'texts': [
            ('Climate','Climate change is a pressing issue. Human activities cause global warming. We must reduce emissions.','Изменение климата — острая проблема. Деятельность человека вызывает глобальное потепление. Мы должны сократить выбросы.'),
        ],
        'pics': ['https://picsum.photos/400/300?9','https://picsum.photos/400/300?10']
    },
    'C1': {
        'words': [
            ('albeit','хотя'),('benevolent','доброжелательный'),('coherent','связный'),
            ('deteriorate','ухудшаться'),('elusive','неуловимый'),('exacerbate','усугублять'),
            ('hypothesis','гипотеза'),('indispensable','необходимый'),
            ('paradigm','парадигма'),('prevalent','распространённый'),
            ('ubiquitous','вездесущий'),('undermine','подрывать'),
            ('unprecedented','беспрецедентный'),('versatile','универсальный'),
        ],
        'phrases': [
            ('At face value','На первый взгляд'),('Bear in mind','Иметь в виду'),
            ('On the brink of','На грани'),('To say the least','Мягко говоря'),
        ],
        'texts': [
            ('Consciousness','Consciousness has puzzled philosophers for centuries. Neuroscience has made progress, but subjective experience remains elusive.','Сознание озадачивало философов веками. Нейронаука добилась прогресса, но субъективный опыт остаётся неуловимым.'),
        ],
        'pics': ['https://picsum.photos/400/300?11','https://picsum.photos/400/300?12']
    }
}

# ===== ГРАММАТИКА =====
GRAMMAR = {
    'Present Simple': 'Регулярные действия.\nI work, He works.\nВопрос: do/does.\nОтрицание: don\'t/doesn\'t.',
    'Present Continuous': 'Действие сейчас.\nI am working.\nam/is/are + V-ing.',
    'Past Simple': 'Прошлое.\nI worked, I went.\nВопрос: did.\nОтрицание: didn\'t.',
    'Future Simple': 'Будущее.\nI will work.\nОтрицание: won\'t.',
    'Articles': 'a/an — неопр.\nthe — опр.\nБез артикля — общее.',
    'Modal Verbs': 'can — могу\nshould — следует\nmust — обязан\nmay — можно',
}

# ===== ФУНКЦИИ =====
def get_level(chat_id):
    return user_levels.get(str(chat_id), 'A1')

def init_user(chat_id):
    if chat_id not in user_points:
        user_points[chat_id] = 0
        user_achievements[chat_id] = []

def add_points(chat_id, points):
    init_user(chat_id)
    user_points[chat_id] += points
    pts = user_points[chat_id]
    ach = user_achievements[chat_id]
    if pts >= 50 and '🎓 Ученик' not in ach:
        ach.append('🎓 Ученик')
        send_message(chat_id, '🏆 Ученик! (50)')
    if pts >= 100 and '📚 Знаток' not in ach:
        ach.append('📚 Знаток')
        send_message(chat_id, '🏆 Знаток! (100)')
    if pts >= 250 and '🧠 Эксперт' not in ach:
        ach.append('🧠 Эксперт')
        send_message(chat_id, '🏆 Эксперт! (250)')
    if pts >= 500 and '👑 Магистр' not in ach:
        ach.append('👑 Магистр')
        send_message(chat_id, '👑 Магистр! (500)')

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = reply_markup
    requests.post(f'{BASE_URL}/sendMessage', json=payload)

def send_photo(chat_id):
    level = get_level(chat_id)
    pics = WORDS[level]['pics']
    url = random.choice(pics)
    requests.post(f'{BASE_URL}/sendPhoto', json={'chat_id': chat_id, 'photo': url, 'caption': f'🖼 Опиши картинку (уровень {level})'})

def send_words(chat_id):
    level = get_level(chat_id)
    words = random.sample(WORDS[level]['words'], min(5, len(WORDS[level]['words'])))
    phrases = random.sample(WORDS[level]['phrases'], min(2, len(WORDS[level]['phrases'])))
    text = f"📚 *Уровень {level}*\n\n"
    for w in words: text += f"• {w[0]} — {w[1]}\n"
    text += "\n*Фразы:*\n"
    for p in phrases: text += f"💬 {p[0]} — {p[1]}\n"
    send_message(chat_id, text, {'inline_keyboard': [[{'text': '🔄 Ещё', 'callback_data': 'more_words'}]]})

def send_test(chat_id):
    level = get_level(chat_id)
    words = WORDS[level]['words']
    if len(words) < 5: send_message(chat_id, 'Мало слов.'); return
    test_words = random.sample(words, 5)
    user_test[str(chat_id)] = {'words': test_words, 'index': 0, 'correct': 0}
    send_next_question(chat_id)

def send_next_question(chat_id):
    test = user_test.get(str(chat_id))
    if not test or test['index'] >= 5:
        if test:
            c = test['correct']
            send_message(chat_id, f'🏆 Тест завершён!\n✅ {c}/5\n📈 {c*20}%')
        if str(chat_id) in user_test: del user_test[str(chat_id)]
        return
    word = test['words'][test['index']]
    all_words = WORDS[get_level(chat_id)]['words']
    options = [word[1]]
    while len(options) < 4:
        r = random.choice(all_words)[1]
        if r not in options: options.append(r)
    random.shuffle(options)
    keyboard = {'inline_keyboard': [[{'text': opt, 'callback_data': f'quiz_{word[1]}_{opt}'}] for opt in options]}
    send_message(chat_id, f"📝 ({test['index']+1}/5) *{word[0]}*", keyboard)

def send_text(chat_id):
    level = get_level(chat_id)
    text_data = random.choice(WORDS[level]['texts'])
    user_last_text[str(chat_id)] = text_data[2]
    user_state[str(chat_id)] = 'waiting_translation'
    send_message(chat_id, f"📖 *{text_data[0]}*\n\n{text_data[1]}\n\n✏️ Переведи и отправь!")

def send_dictation(chat_id):
    level = get_level(chat_id)
    items = WORDS[level]['words'] + WORDS[level]['phrases']
    if not items: return
    item = random.choice(items)
    user_last_text[chat_id] = item[0]
    user_state[chat_id] = 'waiting_dictation'
    send_message(chat_id, f"🎧 *Диктант*\nНапиши: _{item[0]}_")

def send_review(chat_id):
    level = get_level(chat_id)
    words = WORDS[level]['words']
    if len(words) < 1: return
    card = random.choice(words)
    user_review_cards[chat_id] = card
    send_message(chat_id, f"🔁 *Повторение*\nСлово: *{card[0]}*", {'inline_keyboard': [[{'text': 'Показать перевод', 'callback_data': f'review_show_{chat_id}'}]]})

def send_grammar(chat_id):
    topics = list(GRAMMAR.keys())
    keyboard = {'inline_keyboard': [[{'text': t, 'callback_data': f'grammar_{t}'}] for t in topics]}
    send_message(chat_id, '📝 *Грамматика*\nВыбери тему:', keyboard)

def send_stats(chat_id):
    init_user(chat_id)
    pts = user_points[chat_id]
    ach = user_achievements[chat_id]
    lvl = get_level(chat_id)
    text = f'🎮 *Прогресс*\n⭐ Очки: {pts}\n🏆 Достижений: {len(ach)}\n📚 Уровень: {lvl}'
    if ach: text += '\n\n🏅 ' + ' | '.join(ach)
    send_message(chat_id, text)

def send_achievements(chat_id):
    init_user(chat_id)
    ach = user_achievements[chat_id]
    send_message(chat_id, '🏆 *Достижения:*\n\n' + '\n'.join(ach) if ach else 'Пока нет достижений.')

def send_dictionary(chat_id):
    send_message(chat_id, '📖 *Словарь*\nВведи слово на английском или русском — я переведу.')

def search_dictionary(chat_id, query):
    query = query.lower().strip()
    found = []
    for level in ['A1','A2','B1','B2','C1']:
        for w in WORDS[level]['words']:
            en, ru = w[0], w[1]
            if query in en.lower() or query in ru.lower():
                found.append(f'📖 {en} = {ru} [{level}]')
        for p in WORDS[level]['phrases']:
            en, ru = p
            if query in en.lower() or query in ru.lower():
                found.append(f'💬 {en} = {ru} [{level}]')
    if found:
        send_message(chat_id, '\n\n'.join(found[:10]))
    else:
        send_message(chat_id, f'❌ "{query}" не найдено.')

def send_level_menu(chat_id):
    current = get_level(chat_id)
    passed = LEVEL_PASSED.get(chat_id, ['A1'])
    desc = {'A1':'Начинающий','A2':'Элементарный','B1':'Средний','B2':'Выше среднего','C1':'Продвинутый'}
    keyboard = {'inline_keyboard': []}
    for i, lvl in enumerate(LEVEL_ORDER):
        if lvl in passed:
            mark = ' ✅' if lvl == current else ''
            keyboard['inline_keyboard'].append([{'text': f'{lvl} {desc[lvl]}{mark}', 'callback_data': f'setlevel_{lvl}'}])
        elif i > 0 and LEVEL_ORDER[i-1] in passed:
            keyboard['inline_keyboard'].append([{'text': f'📝 Сдать на {lvl}', 'callback_data': f'trylevel_{lvl}'}])
        else:
            keyboard['inline_keyboard'].append([{'text': f'🔒 {lvl} {desc[lvl]}', 'callback_data': 'locked'}])
    send_message(chat_id, f'🎯 Твой уровень: *{current}*', keyboard)

def send_level_test(chat_id, level):
    words = WORDS[level]['words']
    if len(words) < 10: send_message(chat_id, 'Мало слов.'); return
    test_words = random.sample(words, 10)
    LEVEL_TESTS[chat_id] = {'level': level, 'words': test_words, 'index': 0, 'correct': 0}
    send_level_question(chat_id)

def send_level_question(chat_id):
    test = LEVEL_TESTS.get(chat_id)
    if not test: return
    if test['index'] >= 10:
        correct = test['correct']
        level = test['level']
        if correct >= 8:
            if level not in LEVEL_PASSED.get(chat_id, []):
                LEVEL_PASSED.setdefault(chat_id, ['A1']).append(level)
            user_levels[chat_id] = level
            send_message(chat_id, f'🎉 Уровень {level} пройден! ✅ {correct}/10')
        else:
            send_message(chat_id, f'😔 {correct}/10. Нужно 8/10.')
        del LEVEL_TESTS[chat_id]
        return
    word = test['words'][test['index']]
    all_words = WORDS[test['level']]['words']
    options = [word[1]]
    while len(options) < 4:
        r = random.choice(all_words)[1]
        if r not in options: options.append(r)
    random.shuffle(options)
    keyboard = {'inline_keyboard': [[{'text': opt, 'callback_data': f'leveltest_{word[1]}_{opt}'}] for opt in options]}
    send_message(chat_id, f"📝 Уровень {test['level']} ({test['index']+1}/10)\n*{word[0]}*", keyboard)

def process_level_test_answer(chat_id, data, msg_id):
    parts = data.split('_')
    correct, user = parts[1], parts[2]
    test = LEVEL_TESTS.get(chat_id)
    if not test: return
    test['correct'] += 1 if user == correct else 0
    test['index'] += 1
    requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': '✅' if user == correct else f'❌ {correct}'})
    send_level_question(chat_id)

def process_callback(callback_query):
    chat_id = str(callback_query['message']['chat']['id'])
    data = callback_query['data']
    msg_id = callback_query['message']['message_id']
    
    if data == 'more_words': send_words(chat_id)
    elif data.startswith('quiz_'):
        parts = data.split('_')
        correct, user = parts[1], parts[2]
        test = user_test.get(chat_id)
        if test:
            if user == correct: test['correct'] += 1; add_points(chat_id, 2)
            test['index'] += 1
            requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': '✅' if user == correct else f'❌ {correct}'})
            send_next_question(chat_id)
    elif data.startswith('setlevel_'):
        lvl = data.replace('setlevel_', '')
        if lvl in LEVEL_PASSED.get(chat_id, ['A1']): user_levels[chat_id] = lvl
        requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': f'✅ {lvl}'})
    elif data.startswith('trylevel_'):
        send_level_test(chat_id, data.replace('trylevel_', ''))
        requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': 'Начинаю тест...'})
    elif data.startswith('leveltest_'): process_level_test_answer(chat_id, data, msg_id)
    elif data == 'locked':
        requests.post(f'{BASE_URL}/answerCallbackQuery', json={'callback_query_id': callback_query['id'], 'text': '🔒 Закрыто!', 'show_alert': True})
    elif data.startswith('grammar_'):
        topic = data.replace('grammar_', '')
        requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': f'📝 *{topic}*\n\n{GRAMMAR.get(topic, "")}'})
    elif data.startswith('review_show_'):
        card = user_review_cards.get(chat_id)
        if card:
            add_points(chat_id, 1)
            requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': f'🔁 {card[0]} = *{card[1]}*\n+1 очко!'})

def process_message(msg):
    chat_id = str(msg['chat']['id'])
    text = msg.get('text', '').strip()
    
    init_user(chat_id)
    LEVEL_PASSED.setdefault(chat_id, ['A1'])
    
    if user_state.get(chat_id) == 'waiting_translation':
        user_state[chat_id] = None
        add_points(chat_id, 5)
        send_message(chat_id, f'📖 Твой перевод:\n{text}\n\n✅ Пример:\n{user_last_text.get(chat_id, "")}\n\n+5 очков!')
        return
    
    if user_state.get(chat_id) == 'waiting_dictation':
        user_state[chat_id] = None
        correct = user_last_text.get(chat_id, '')
        if text.lower().strip() == correct.lower().strip():
            add_points(chat_id, 10)
            send_message(chat_id, '✅ Правильно! +10!')
        else:
            send_message(chat_id, f'❌ Ответ: {correct}')
        return
    
    if text == '/start':
        send_message(chat_id, '🇬🇧 Привет! Я твой тренажёр английского!')
        send_menu(chat_id)
    elif text in ['📚 Слова','/words']: send_words(chat_id)
    elif text in ['📝 Тест','/test']: send_test(chat_id)
    elif text in ['📖 Текст','/text']: send_text(chat_id)
    elif text in ['🖼 Картинки','/pic']: send_photo(chat_id)
    elif text in ['📖 Словарь','/dict']: send_dictionary(chat_id)
    elif text in ['🎯 Уровень','/level']: send_level_menu(chat_id)
    elif text in ['🎮 Прогресс','/stats']: send_stats(chat_id)
    elif text in ['📝 Грамматика','/grammar']: send_grammar(chat_id)
    elif text in ['🎧 Диктант','/dictation']: send_dictation(chat_id)
    elif text in ['🔁 Повторение','/repeat']: send_review(chat_id)
    elif text in ['🏆 Достижения','/achievements']: send_achievements(chat_id)
    elif text == '❓ Помощь':
        send_message(chat_id, '📚 Слова\n📝 Тест\n📖 Текст\n🖼 Картинки\n📖 Словарь\n🎯 Уровень\n🎮 Прогресс\n📝 Грамматика\n🎧 Диктант\n🔁 Повторение')
    else: search_dictionary(chat_id, text)

def send_menu(chat_id):
    keyboard = {'keyboard': [
        [{'text':'📚 Слова'},{'text':'📝 Тест'}],
        [{'text':'📖 Текст'},{'text':'🖼 Картинки'}],
        [{'text':'📖 Словарь'},{'text':'🎯 Уровень'}],
        [{'text':'🎮 Прогресс'},{'text':'📝 Грамматика'}],
        [{'text':'🎧 Диктант'},{'text':'🔁 Повторение'}],
        [{'text':'🏆 Достижения'},{'text':'❓ Помощь'}]
    ], 'resize_keyboard': True}
    send_message(chat_id, '📍 Меню:', keyboard)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'callback_query' in data: process_callback(data['callback_query'])
    elif 'message' in data: process_message(data['message'])
    return 'ok', 200

@app.route('/')
def home():
    return 'English Bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
