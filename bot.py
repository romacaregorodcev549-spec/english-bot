import os
import json
import random
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = '8609800555:AAGO33Tub9bYSxskT92HWGvYdASaFWzW5Gs'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# База знаний
WORDS = {
    'A1': {
        'words': [
            ('apple', 'яблоко', 'Еда'), ('bread', 'хлеб', 'Еда'), ('water', 'вода', 'Еда'),
            ('milk', 'молоко', 'Еда'), ('egg', 'яйцо', 'Еда'), ('fish', 'рыба', 'Еда'),
            ('cat', 'кот', 'Животные'), ('dog', 'собака', 'Животные'), ('bird', 'птица', 'Животные'),
            ('house', 'дом', 'Дом'), ('table', 'стол', 'Дом'), ('chair', 'стул', 'Дом'),
            ('book', 'книга', 'Учёба'), ('car', 'машина', 'Транспорт'), ('bus', 'автобус', 'Транспорт'),
            ('red', 'красный', 'Цвета'), ('blue', 'синий', 'Цвета'), ('green', 'зелёный', 'Цвета'),
            ('big', 'большой', 'Прил'), ('small', 'маленький', 'Прил'), ('good', 'хороший', 'Прил'),
            ('friend', 'друг', 'Люди'), ('family', 'семья', 'Люди'), ('mother', 'мама', 'Люди'),
            ('father', 'папа', 'Люди'), ('time', 'время', 'Общее'), ('day', 'день', 'Общее'),
            ('sun', 'солнце', 'Природа'), ('moon', 'луна', 'Природа'), ('star', 'звезда', 'Природа')
        ],
        'phrases': [
            ('Hello', 'Привет'), ('Good morning', 'Доброе утро'), ('How are you?', 'Как дела?'),
            ('Thank you', 'Спасибо'), ('I like it', 'Мне нравится')
        ],
        'texts': [
            'My name is Tom. I am 10 years old. I have a cat. I love my family.',
            'I wake up at 7. I eat breakfast. I go to school. I like school.'
        ]
    },
    'A2': {
        'words': [
            ('market', 'рынок', 'Еда'), ('sugar', 'сахар', 'Еда'), ('vegetable', 'овощ', 'Еда'),
            ('fruit', 'фрукт', 'Еда'), ('chicken', 'курица', 'Еда'), ('weather', 'погода', 'Природа'),
            ('snow', 'снег', 'Природа'), ('river', 'река', 'Природа'), ('mountain', 'гора', 'Природа'),
            ('hospital', 'больница', 'Город'), ('shop', 'магазин', 'Город'), ('bank', 'банк', 'Город'),
            ('clothes', 'одежда', 'Одежда'), ('shirt', 'рубашка', 'Одежда'), ('dress', 'платье', 'Одежда'),
            ('music', 'музыка', 'Развл'), ('film', 'фильм', 'Развл'), ('sport', 'спорт', 'Развл'),
            ('work', 'работа', 'Работа'), ('office', 'офис', 'Работа'), ('money', 'деньги', 'Работа'),
            ('cheap', 'дешёвый', 'Прил'), ('expensive', 'дорогой', 'Прил'), ('happy', 'счастливый', 'Прил'),
            ('sad', 'грустный', 'Прил'), ('hungry', 'голодный', 'Прил'), ('tired', 'уставший', 'Прил')
        ],
        'phrases': [
            ('What time is it?', 'Который час?'), ('How much?', 'Сколько стоит?'),
            ('Can you help?', 'Можете помочь?'), ('in my opinion', 'по моему мнению')
        ],
        'texts': [
            'Last weekend I went to the park. The weather was sunny. We played football. It was great!',
            'Yesterday I went shopping. I bought a shirt and shoes. I am happy.'
        ]
    },
    'B1': {
        'words': [
            ('achievement', 'достижение'), ('advantage', 'преимущество'), ('advice', 'совет'),
            ('behaviour', 'поведение'), ('challenge', 'вызов'), ('choice', 'выбор'),
            ('communication', 'общение'), ('community', 'сообщество'), ('culture', 'культура'),
            ('decision', 'решение'), ('education', 'образование'), ('environment', 'окружающая среда'),
            ('experience', 'опыт'), ('freedom', 'свобода'), ('health', 'здоровье'),
            ('knowledge', 'знание'), ('opportunity', 'возможность'), ('patience', 'терпение')
        ],
        'phrases': [
            ('As a result', 'В результате'), ('In addition', 'Кроме того'),
            ('On the contrary', 'Наоборот'), ('In conclusion', 'В заключение')
        ],
        'texts': [
            'Technology has changed our lives. People use smartphones for work and entertainment. However, spending too much time on devices can have negative effects on health.'
        ]
    },
    'B2': {
        'words': [
            ('abundant', 'обильный'), ('accurate', 'точный'), ('appropriate', 'подходящий'),
            ('comprehensive', 'всесторонний'), ('crucial', 'решающий'), ('diverse', 'разнообразный'),
            ('efficient', 'эффективный'), ('evidence', 'доказательство'), ('fundamental', 'фундаментальный'),
            ('implement', 'осуществлять'), ('inevitable', 'неизбежный'), ('maintain', 'поддерживать'),
            ('outcome', 'исход'), ('significant', 'значительный'), ('sufficient', 'достаточный')
        ],
        'phrases': [
            ('As a matter of fact', 'На самом деле'), ('In the long run', 'В долгосрочной перспективе'),
            ('On the whole', 'В целом'), ('Without a doubt', 'Без сомнения')
        ],
        'texts': [
            'Climate change is one of the most pressing issues of our time. Scientists agree that human activities are responsible for global warming.'
        ]
    },
    'C1': {
        'words': [
            ('albeit', 'хотя'), ('benevolent', 'доброжелательный'), ('coherent', 'связный'),
            ('deteriorate', 'ухудшаться'), ('elusive', 'неуловимый'), ('exacerbate', 'усугублять'),
            ('hypothesis', 'гипотеза'), ('indispensable', 'необходимый'), ('paradigm', 'парадигма'),
            ('prevalent', 'распространённый'), ('ubiquitous', 'вездесущий'), ('undermine', 'подрывать'),
            ('unprecedented', 'беспрецедентный'), ('versatile', 'универсальный')
        ],
        'phrases': [
            ('At face value', 'На первый взгляд'), ('Bear in mind', 'Иметь в виду'),
            ('On the brink of', 'На грани'), ('To say the least', 'Мягко говоря')
        ],
        'texts': [
            'The concept of consciousness has puzzled philosophers for centuries. While neuroscience has made progress, the subjective nature of experience remains elusive.'
        ]
    }
}

# Хранилище уровней пользователей (в памяти)
user_levels = {}

def get_level(chat_id):
    return user_levels.get(str(chat_id), 'A1')

def set_level(chat_id, level):
    user_levels[str(chat_id)] = level

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = reply_markup
    requests.post(f'{BASE_URL}/sendMessage', json=payload)

def send_photo(chat_id, caption=''):
    pics = ['https://picsum.photos/400/300?nature', 'https://picsum.photos/400/300?city',
            'https://picsum.photos/400/300?food', 'https://picsum.photos/400/300?animals']
    url = random.choice(pics)
    requests.post(f'{BASE_URL}/sendPhoto', json={
        'chat_id': chat_id, 'photo': url,
        'caption': caption or 'Опиши, что видишь на картинке!'
    })

def send_words(chat_id):
    level = get_level(chat_id)
    words = random.sample(WORDS[level]['words'], min(5, len(WORDS[level]['words'])))
    text = f"📚 *Уровень {level}*\n\n"
    for w in words:
        text += f"• {w[0]} — {w[1]} ({w[2]})\n"
    
    keyboard = {
        'inline_keyboard': [[{'text': '🔄 Ещё 5 слов', 'callback_data': 'more_words'}]]
    }
    send_message(chat_id, text, keyboard)

def send_test(chat_id):
    level = get_level(chat_id)
    all_words = WORDS[level]['words']
    
    if len(all_words) < 4:
        send_message(chat_id, 'Мало слов для теста. Смени уровень.')
        return
    
    word = random.choice(all_words)
    correct = word[1]
    
    options = [correct]
    while len(options) < 4:
        r = random.choice(all_words)[1]
        if r not in options:
            options.append(r)
    random.shuffle(options)
    
    correct_idx = options.index(correct)
    
    keyboard = {
        'inline_keyboard': [[{'text': opt, 'callback_data': f'test_{correct}_{opt}'}] for opt in options]
    }
    send_message(chat_id, f"📝 Как переводится: *{word[0]}*?", keyboard)

def send_text(chat_id):
    level = get_level(chat_id)
    text = random.choice(WORDS[level]['texts'])
    send_message(chat_id, f"📖 *Текст (уровень {level}):*\n\n{text}")

def send_level_menu(chat_id):
    level = get_level(chat_id)
    desc = {'A1': 'Начинающий', 'A2': 'Элементарный', 'B1': 'Средний',
            'B2': 'Выше среднего', 'C1': 'Продвинутый'}
    
    keyboard = {
        'inline_keyboard': [
            [{'text': f"{l} {desc[l]}{' ✅' if level == l else ''}", 'callback_data': f'level_{l}'}]
            for l in ['A1', 'A2', 'B1', 'B2', 'C1']
        ]
    }
    send_message(chat_id, f"🎯 Твой уровень: *{level}* — {desc[level]}\nВыбери новый:", keyboard)

def process_callback(callback_query):
    chat_id = callback_query['message']['chat']['id']
    data = callback_query['data']
    msg_id = callback_query['message']['message_id']
    
    if data == 'more_words':
        send_words(chat_id)
    elif data.startswith('test_'):
        parts = data.split('_')
        correct = parts[1]
        user_answer = parts[2]
        
        if user_answer == correct:
            requests.post(f'{BASE_URL}/editMessageText', json={
                'chat_id': chat_id, 'message_id': msg_id,
                'text': '✅ Правильно!'
            })
        else:
            requests.post(f'{BASE_URL}/editMessageText', json={
                'chat_id': chat_id, 'message_id': msg_id,
                'text': f'❌ Неправильно. Ответ: {correct}'
            })
    elif data.startswith('level_'):
        level = data.replace('level_', '')
        set_level(chat_id, level)
        requests.post(f'{BASE_URL}/editMessageText', json={
            'chat_id': chat_id, 'message_id': msg_id,
            'text': f'✅ Уровень изменён на {level}'
        })

def process_message(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip()
    
    if text == '/start':
        send_message(chat_id, '🇬🇧 Привет! Я твой тренажёр английского!')
        send_menu(chat_id)
    elif text in ['📚 Слова', '/words']:
        send_words(chat_id)
    elif text in ['📝 Тест', '/test']:
        send_test(chat_id)
    elif text in ['📖 Текст', '/text']:
        send_text(chat_id)
    elif text in ['🖼 Картинки', '/pic']:
        send_photo(chat_id)
    elif text in ['🎯 Уровень', '/level']:
        send_level_menu(chat_id)
    elif text == '❓ Помощь':
        send_message(chat_id, '📚 Слова — изучение\n📝 Тест — проверка\n📖 Текст — чтение\n🖼 Картинки — визуально\n🎯 Уровень — A1-C1')
    else:
        # Проверяем слово в словаре
        level = get_level(chat_id)
        for w in WORDS[level]['words']:
            if text.lower() == w[0].lower():
                send_message(chat_id, f'📖 {w[0]} = {w[1]} ({w[2]})')
                return
        send_message(chat_id, 'Используй меню или напиши слово на английском.')

def send_menu(chat_id):
    keyboard = {
        'keyboard': [
            [{'text': '📚 Слова'}, {'text': '📝 Тест'}],
            [{'text': '📖 Текст'}, {'text': '🖼 Картинки'}],
            [{'text': '🎯 Уровень'}, {'text': '❓ Помощь'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, '📍 Меню:', keyboard)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'callback_query' in data:
        process_callback(data['callback_query'])
    elif 'message' in data:
        process_message(data['message'])
    return 'ok', 200

@app.route('/')
def home():
    return 'English Bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))