import os
import json
import random
from flask import Flask, request
import requests
import asyncio
import tempfile
import edge_tts

app = Flask(__name__)

TOKEN = '8609800555:AAGO33Tub9bYSxskT92HWGvYdASaFWzW5Gs'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# Состояние пользователей
user_state = {}  # 'waiting_translation' или None
user_last_text = {}  # последний текст для проверки перевода
user_levels = {}
user_test = {}  # данные теста

WORDS = {
    'A1': {
        'words': [
            # Еда и напитки
            ('apple', 'яблоко', 'Еда'), ('banana', 'банан', 'Еда'), ('bread', 'хлеб', 'Еда'),
            ('water', 'вода', 'Еда'), ('milk', 'молоко', 'Еда'), ('egg', 'яйцо', 'Еда'),
            ('fish', 'рыба', 'Еда'), ('meat', 'мясо', 'Еда'), ('rice', 'рис', 'Еда'),
            ('soup', 'суп', 'Еда'), ('cake', 'торт', 'Еда'), ('juice', 'сок', 'Еда'),
            ('tea', 'чай', 'Еда'), ('coffee', 'кофе', 'Еда'), ('sugar', 'сахар', 'Еда'),
            ('salt', 'соль', 'Еда'), ('cheese', 'сыр', 'Еда'), ('butter', 'масло', 'Еда'),
            ('chicken', 'курица', 'Еда'), ('salad', 'салат', 'Еда'), ('pizza', 'пицца', 'Еда'),
            ('sandwich', 'бутерброд', 'Еда'), ('chocolate', 'шоколад', 'Еда'), ('ice cream', 'мороженое', 'Еда'),
            ('cookie', 'печенье', 'Еда'), ('orange', 'апельсин', 'Еда'), ('lemon', 'лимон', 'Еда'),
            ('tomato', 'помидор', 'Еда'), ('potato', 'картофель', 'Еда'), ('carrot', 'морковь', 'Еда'),
            # Животные
            ('cat', 'кот', 'Животные'), ('dog', 'собака', 'Животные'), ('bird', 'птица', 'Животные'),
            ('horse', 'лошадь', 'Животные'), ('cow', 'корова', 'Животные'), ('pig', 'свинья', 'Животные'),
            ('sheep', 'овца', 'Животные'), ('rabbit', 'кролик', 'Животные'), ('mouse', 'мышь', 'Животные'),
            ('bear', 'медведь', 'Животные'), ('lion', 'лев', 'Животные'), ('tiger', 'тигр', 'Животные'),
            ('elephant', 'слон', 'Животные'), ('monkey', 'обезьяна', 'Животные'), ('snake', 'змея', 'Животные'),
            ('frog', 'лягушка', 'Животные'), ('duck', 'утка', 'Животные'), ('hen', 'курица', 'Животные'),
            # Дом и быт
            ('house', 'дом', 'Дом'), ('room', 'комната', 'Дом'), ('door', 'дверь', 'Дом'),
            ('window', 'окно', 'Дом'), ('table', 'стол', 'Дом'), ('chair', 'стул', 'Дом'),
            ('bed', 'кровать', 'Дом'), ('kitchen', 'кухня', 'Дом'), ('bathroom', 'ванная', 'Дом'),
            ('garden', 'сад', 'Дом'), ('floor', 'пол', 'Дом'), ('wall', 'стена', 'Дом'),
            ('roof', 'крыша', 'Дом'), ('stairs', 'лестница', 'Дом'), ('mirror', 'зеркало', 'Дом'),
            ('sofa', 'диван', 'Дом'), ('lamp', 'лампа', 'Дом'), ('clock', 'часы', 'Дом'),
            ('key', 'ключ', 'Дом'), ('phone', 'телефон', 'Дом'), ('computer', 'компьютер', 'Дом'),
            # Одежда
            ('shirt', 'рубашка', 'Одежда'), ('dress', 'платье', 'Одежда'), ('shoes', 'обувь', 'Одежда'),
            ('hat', 'шляпа', 'Одежда'), ('coat', 'пальто', 'Одежда'), ('jacket', 'куртка', 'Одежда'),
            ('socks', 'носки', 'Одежда'), ('skirt', 'юбка', 'Одежда'), ('jeans', 'джинсы', 'Одежда'),
            ('sweater', 'свитер', 'Одежда'), ('boots', 'ботинки', 'Одежда'), ('gloves', 'перчатки', 'Одежда'),
            ('scarf', 'шарф', 'Одежда'), ('belt', 'ремень', 'Одежда'), ('pocket', 'карман', 'Одежда'),
            # Цвета
            ('red', 'красный', 'Цвета'), ('blue', 'синий', 'Цвета'), ('green', 'зелёный', 'Цвета'),
            ('yellow', 'жёлтый', 'Цвета'), ('white', 'белый', 'Цвета'), ('black', 'чёрный', 'Цвета'),
            ('brown', 'коричневый', 'Цвета'), ('grey', 'серый', 'Цвета'), ('pink', 'розовый', 'Цвета'),
            ('purple', 'фиолетовый', 'Цвета'), ('orange', 'оранжевый', 'Цвета'), ('gold', 'золотой', 'Цвета'),
            # Прилагательные
            ('big', 'большой', 'Прил'), ('small', 'маленький', 'Прил'), ('good', 'хороший', 'Прил'),
            ('bad', 'плохой', 'Прил'), ('new', 'новый', 'Прил'), ('old', 'старый', 'Прил'),
            ('hot', 'горячий', 'Прил'), ('cold', 'холодный', 'Прил'), ('fast', 'быстрый', 'Прил'),
            ('slow', 'медленный', 'Прил'), ('easy', 'лёгкий', 'Прил'), ('hard', 'сложный', 'Прил'),
            ('happy', 'счастливый', 'Прил'), ('sad', 'грустный', 'Прил'), ('hungry', 'голодный', 'Прил'),
            ('thirsty', 'жаждущий', 'Прил'), ('tired', 'уставший', 'Прил'), ('beautiful', 'красивый', 'Прил'),
            ('ugly', 'уродливый', 'Прил'), ('clean', 'чистый', 'Прил'), ('dirty', 'грязный', 'Прил'),
            ('rich', 'богатый', 'Прил'), ('poor', 'бедный', 'Прил'), ('strong', 'сильный', 'Прил'),
            ('weak', 'слабый', 'Прил'), ('long', 'длинный', 'Прил'), ('short', 'короткий', 'Прил'),
            # Люди и семья
            ('friend', 'друг', 'Люди'), ('family', 'семья', 'Люди'), ('mother', 'мама', 'Люди'),
            ('father', 'папа', 'Люди'), ('brother', 'брат', 'Люди'), ('sister', 'сестра', 'Люди'),
            ('baby', 'ребёнок', 'Люди'), ('man', 'мужчина', 'Люди'), ('woman', 'женщина', 'Люди'),
            ('boy', 'мальчик', 'Люди'), ('girl', 'девочка', 'Люди'), ('son', 'сын', 'Люди'),
            ('daughter', 'дочь', 'Люди'), ('husband', 'муж', 'Люди'), ('wife', 'жена', 'Люди'),
            ('neighbour', 'сосед', 'Люди'), ('teacher', 'учитель', 'Люди'), ('student', 'студент', 'Люди'),
            ('doctor', 'врач', 'Люди'), ('nurse', 'медсестра', 'Люди'), ('driver', 'водитель', 'Люди'),
            # Время и даты
            ('time', 'время', 'Время'), ('day', 'день', 'Время'), ('night', 'ночь', 'Время'),
            ('morning', 'утро', 'Время'), ('evening', 'вечер', 'Время'), ('week', 'неделя', 'Время'),
            ('month', 'месяц', 'Время'), ('year', 'год', 'Время'), ('today', 'сегодня', 'Время'),
            ('tomorrow', 'завтра', 'Время'), ('yesterday', 'вчера', 'Время'), ('hour', 'час', 'Время'),
            ('minute', 'минута', 'Время'), ('second', 'секунда', 'Время'), ('Monday', 'понедельник', 'Время'),
            ('Tuesday', 'вторник', 'Время'), ('Wednesday', 'среда', 'Время'), ('Thursday', 'четверг', 'Время'),
            ('Friday', 'пятница', 'Время'), ('Saturday', 'суббота', 'Время'), ('Sunday', 'воскресенье', 'Время'),
            # Природа
            ('sun', 'солнце', 'Природа'), ('moon', 'луна', 'Природа'), ('star', 'звезда', 'Природа'),
            ('tree', 'дерево', 'Природа'), ('flower', 'цветок', 'Природа'), ('rain', 'дождь', 'Природа'),
            ('snow', 'снег', 'Природа'), ('wind', 'ветер', 'Природа'), ('river', 'река', 'Природа'),
            ('mountain', 'гора', 'Природа'), ('sea', 'море', 'Природа'), ('lake', 'озеро', 'Природа'),
            ('forest', 'лес', 'Природа'), ('sky', 'небо', 'Природа'), ('cloud', 'облако', 'Природа'),
            ('fire', 'огонь', 'Природа'), ('stone', 'камень', 'Природа'), ('grass', 'трава', 'Природа'),
            # Транспорт и город
            ('car', 'машина', 'Транспорт'), ('bus', 'автобус', 'Транспорт'), ('train', 'поезд', 'Транспорт'),
            ('bike', 'велосипед', 'Транспорт'), ('plane', 'самолёт', 'Транспорт'), ('boat', 'лодка', 'Транспорт'),
            ('taxi', 'такси', 'Транспорт'), ('street', 'улица', 'Город'), ('road', 'дорога', 'Город'),
            ('shop', 'магазин', 'Город'), ('hospital', 'больница', 'Город'), ('bank', 'банк', 'Город'),
            ('park', 'парк', 'Город'), ('bridge', 'мост', 'Город'), ('hotel', 'отель', 'Город'),
            ('restaurant', 'ресторан', 'Город'), ('cinema', 'кинотеатр', 'Город'), ('museum', 'музей', 'Город'),
            # Глаголы
            ('go', 'идти', 'Глаголы'), ('come', 'приходить', 'Глаголы'), ('eat', 'есть', 'Глаголы'),
            ('drink', 'пить', 'Глаголы'), ('sleep', 'спать', 'Глаголы'), ('run', 'бегать', 'Глаголы'),
            ('walk', 'гулять', 'Глаголы'), ('sit', 'сидеть', 'Глаголы'), ('stand', 'стоять', 'Глаголы'),
            ('see', 'видеть', 'Глаголы'), ('hear', 'слышать', 'Глаголы'), ('speak', 'говорить', 'Глаголы'),
            ('read', 'читать', 'Глаголы'), ('write', 'писать', 'Глаголы'), ('sing', 'петь', 'Глаголы'),
            ('dance', 'танцевать', 'Глаголы'), ('play', 'играть', 'Глаголы'), ('work', 'работать', 'Глаголы'),
            ('study', 'учиться', 'Глаголы'), ('buy', 'покупать', 'Глаголы'), ('sell', 'продавать', 'Глаголы'),
            ('open', 'открыть', 'Глаголы'), ('close', 'закрыть', 'Глаголы'), ('like', 'нравиться', 'Глаголы'),
            ('love', 'любить', 'Глаголы'), ('hate', 'ненавидеть', 'Глаголы'), ('want', 'хотеть', 'Глаголы'),
            ('need', 'нуждаться', 'Глаголы'), ('give', 'давать', 'Глаголы'), ('take', 'брать', 'Глаголы'),
            # Числа и количества
            ('one', 'один', 'Числа'), ('two', 'два', 'Числа'), ('three', 'три', 'Числа'),
            ('four', 'четыре', 'Числа'), ('five', 'пять', 'Числа'), ('six', 'шесть', 'Числа'),
            ('seven', 'семь', 'Числа'), ('eight', 'восемь', 'Числа'), ('nine', 'девять', 'Числа'),
            ('ten', 'десять', 'Числа'), ('first', 'первый', 'Числа'), ('last', 'последний', 'Числа'),
            ('many', 'много', 'Числа'), ('few', 'мало', 'Числа'), ('some', 'несколько', 'Числа'),
            ('all', 'все', 'Числа'), ('every', 'каждый', 'Числа'), ('each', 'каждый', 'Числа'),
            # Части тела
            ('head', 'голова', 'Тело'), ('hand', 'рука', 'Тело'), ('foot', 'нога', 'Тело'),
            ('eye', 'глаз', 'Тело'), ('ear', 'ухо', 'Тело'), ('nose', 'нос', 'Тело'),
            ('mouth', 'рот', 'Тело'), ('hair', 'волосы', 'Тело'), ('finger', 'палец', 'Тело'),
            ('arm', 'рука', 'Тело'), ('leg', 'нога', 'Тело'), ('back', 'спина', 'Тело'),
            ('heart', 'сердце', 'Тело'), ('face', 'лицо', 'Тело'), ('tooth', 'зуб', 'Тело'),
            ('teeth', 'зубы', 'Тело'), ('tongue', 'язык', 'Тело'), ('neck', 'шея', 'Тело'),
        ],
        'phrases': [
            # Приветствия и знакомство
            ('Hello', 'Привет'),
            ('Hi', 'Привет'),
            ('Good morning', 'Доброе утро'),
            ('Good afternoon', 'Добрый день'),
            ('Good evening', 'Добрый вечер'),
            ('Good night', 'Спокойной ночи'),
            ('Goodbye', 'До свидания'),
            ('Bye', 'Пока'),
            ('See you later', 'Увидимся позже'),
            ('See you tomorrow', 'Увидимся завтра'),
            ('How are you?', 'Как дела?'),
            ('I am fine', 'Я в порядке'),
            ('I am OK', 'Я нормально'),
            ('Thank you', 'Спасибо'),
            ('Thanks', 'Спасибо'),
            ('You are welcome', 'Пожалуйста'),
            ('Please', 'Пожалуйста'),
            ('Excuse me', 'Извините'),
            ('I am sorry', 'Прости'),
            ('My name is...', 'Меня зовут...'),
            ('What is your name?', 'Как тебя зовут?'),
            ('Nice to meet you', 'Приятно познакомиться'),
            ('Where are you from?', 'Откуда ты?'),
            ('I am from Russia', 'Я из России'),
            ('How old are you?', 'Сколько тебе лет?'),
            ('I am 20 years old', 'Мне 20 лет'),
            # Повседневные фразы
            ('I like it', 'Мне нравится'),
            ('I don\'t like it', 'Мне не нравится'),
            ('I know', 'Я знаю'),
            ('I don\'t know', 'Я не знаю'),
            ('I understand', 'Я понимаю'),
            ('I don\'t understand', 'Я не понимаю'),
            ('Can you help me?', 'Можете помочь?'),
            ('Help me please', 'Помогите пожалуйста'),
            ('What is this?', 'Что это?'),
            ('What is that?', 'Что то?'),
            ('How much?', 'Сколько?'),
            ('How many?', 'Сколько?'),
            ('Where is the toilet?', 'Где туалет?'),
            ('I am hungry', 'Я голоден'),
            ('I am thirsty', 'Я хочу пить'),
            ('I am tired', 'Я устал'),
            ('I am happy', 'Я счастлив'),
            ('I am sad', 'Мне грустно'),
            ('I am sick', 'Я болен'),
            ('I need a doctor', 'Мне нужен врач'),
            # Вопросы
            ('What?', 'Что?'),
            ('Where?', 'Где?'),
            ('When?', 'Когда?'),
            ('Why?', 'Почему?'),
            ('Who?', 'Кто?'),
            ('How?', 'Как?'),
            ('Which?', 'Который?'),
            ('Whose?', 'Чей?'),
        ],
        'texts': [
            ('My Day', 'I wake up at 7 o\'clock. I eat breakfast. I go to work. I like my job. I come home at 6. I have dinner. I watch TV. I go to bed at 11.', 'Я просыпаюсь в 7 часов. Я завтракаю. Я иду на работу. Мне нравится моя работа. Я прихожу домой в 6. Я ужинаю. Я смотрю телевизор. Я ложусь спать в 11.'),
            ('My Family', 'My name is Tom. I am 25 years old. I have a big family: mother, father, brother and sister. We live in a house. I love my family very much.', 'Меня зовут Том. Мне 25 лет. У меня большая семья: мама, папа, брат и сестра. Мы живём в доме. Я очень люблю свою семью.'),
            ('At the Shop', 'I go to the shop. I buy bread, milk and eggs. The bread is cheap. The milk is fresh. I pay money. I go home.', 'Я иду в магазин. Я покупаю хлеб, молоко и яйца. Хлеб дешёвый. Молоко свежее. Я плачу деньги. Я иду домой.'),
        ],
        'pics': [
            'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400',
            'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=400',
            'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400',
            'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400',
            'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=400',
            'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400',
        ]
    },
    'A2': {
        'words': [
            # Еда
            ('market', 'рынок', 'Еда'), ('vegetable', 'овощ', 'Еда'), ('fruit', 'фрукт', 'Еда'),
            ('dinner', 'ужин', 'Еда'), ('breakfast', 'завтрак', 'Еда'), ('lunch', 'обед', 'Еда'),
            ('steak', 'стейк', 'Еда'), ('pasta', 'паста', 'Еда'), ('sausage', 'сосиска', 'Еда'),
            ('ham', 'ветчина', 'Еда'), ('flour', 'мука', 'Еда'), ('oil', 'масло', 'Еда'),
            ('vinegar', 'уксус', 'Еда'), ('spice', 'специя', 'Еда'), ('garlic', 'чеснок', 'Еда'),
            ('onion', 'лук', 'Еда'), ('pepper', 'перец', 'Еда'), ('cucumber', 'огурец', 'Еда'),
            # Погода и природа
            ('weather', 'погода', 'Природа'), ('storm', 'шторм', 'Природа'), ('fog', 'туман', 'Природа'),
            ('ice', 'лёд', 'Природа'), ('ocean', 'океан', 'Природа'), ('island', 'остров', 'Природа'),
            ('beach', 'пляж', 'Природа'), ('desert', 'пустыня', 'Природа'), ('field', 'поле', 'Природа'),
            ('hill', 'холм', 'Природа'), ('valley', 'долина', 'Природа'), ('waterfall', 'водопад', 'Природа'),
            ('earth', 'земля', 'Природа'), ('planet', 'планета', 'Природа'), ('space', 'космос', 'Природа'),
            # Профессии и работа
            ('job', 'работа', 'Работа'), ('salary', 'зарплата', 'Работа'), ('boss', 'начальник', 'Работа'),
            ('colleague', 'коллега', 'Работа'), ('meeting', 'встреча', 'Работа'), ('project', 'проект', 'Работа'),
            ('company', 'компания', 'Работа'), ('factory', 'завод', 'Работа'), ('business', 'бизнес', 'Работа'),
            ('customer', 'клиент', 'Работа'), ('manager', 'менеджер', 'Работа'), ('engineer', 'инженер', 'Работа'),
            ('pilot', 'пилот', 'Работа'), ('chef', 'шеф-повар', 'Работа'), ('artist', 'художник', 'Работа'),
            ('musician', 'музыкант', 'Работа'), ('writer', 'писатель', 'Работа'), ('actor', 'актёр', 'Работа'),
            # Здоровье
            ('health', 'здоровье', 'Здоровье'), ('medicine', 'лекарство', 'Здоровье'), ('pill', 'таблетка', 'Здоровье'),
            ('pain', 'боль', 'Здоровье'), ('fever', 'жар', 'Здоровье'), ('cough', 'кашель', 'Здоровье'),
            ('headache', 'головная боль', 'Здоровье'), ('accident', 'авария', 'Здоровье'), ('ambulance', 'скорая помощь', 'Здоровье'),
            ('dentist', 'дантист', 'Здоровье'), ('prescription', 'рецепт', 'Здоровье'), ('pharmacy', 'аптека', 'Здоровье'),
            # Прилагательные
            ('cheap', 'дешёвый', 'Прил'), ('expensive', 'дорогой', 'Прил'), ('difficult', 'сложный', 'Прил'),
            ('important', 'важный', 'Прил'), ('interesting', 'интересный', 'Прил'), ('boring', 'скучный', 'Прил'),
            ('popular', 'популярный', 'Прил'), ('famous', 'известный', 'Прил'), ('comfortable', 'удобный', 'Прил'),
            ('dangerous', 'опасный', 'Прил'), ('safe', 'безопасный', 'Прил'), ('possible', 'возможный', 'Прил'),
            ('impossible', 'невозможный', 'Прил'), ('useful', 'полезный', 'Прил'), ('useless', 'бесполезный', 'Прил'),
            ('serious', 'серьёзный', 'Прил'), ('funny', 'смешной', 'Прил'), ('kind', 'добрый', 'Прил'),
            ('angry', 'злой', 'Прил'), ('brave', 'храбрый', 'Прил'), ('shy', 'застенчивый', 'Прил'),
            ('lazy', 'ленивый', 'Прил'), ('clever', 'умный', 'Прил'), ('stupid', 'глупый', 'Прил'),
            # Глаголы
            ('think', 'думать', 'Глаголы'), ('believe', 'верить', 'Глаголы'), ('hope', 'надеяться', 'Глаголы'),
            ('wish', 'желать', 'Глаголы'), ('try', 'пытаться', 'Глаголы'), ('change', 'менять', 'Глаголы'),
            ('become', 'становиться', 'Глаголы'), ('begin', 'начинать', 'Глаголы'), ('finish', 'заканчивать', 'Глаголы'),
            ('stop', 'останавливать', 'Глаголы'), ('start', 'начинать', 'Глаголы'), ('keep', 'продолжать', 'Глаголы'),
            ('put', 'класть', 'Глаголы'), ('bring', 'приносить', 'Глаголы'), ('send', 'отправлять', 'Глаголы'),
            ('receive', 'получать', 'Глаголы'), ('show', 'показывать', 'Глаголы'), ('tell', 'рассказывать', 'Глаголы'),
            ('ask', 'спрашивать', 'Глаголы'), ('answer', 'отвечать', 'Глаголы'), ('explain', 'объяснять', 'Глаголы'),
            ('agree', 'соглашаться', 'Глаголы'), ('refuse', 'отказываться', 'Глаголы'), ('forget', 'забывать', 'Глаголы'),
            ('remember', 'помнить', 'Глаголы'), ('learn', 'учить', 'Глаголы'), ('teach', 'преподавать', 'Глаголы'),
        ],
        'phrases': [
            ('What time is it?', 'Который час?'),
            ('It is half past two', 'Половина третьего'),
            ('I would like a coffee', 'Я бы хотел кофе'),
            ('Could I have the bill?', 'Можно счёт?'),
            ('How much is it?', 'Сколько это стоит?'),
            ('It is too expensive', 'Слишком дорого'),
            ('Can I pay by card?', 'Можно оплатить картой?'),
            ('What do you do?', 'Чем вы занимаетесь?'),
            ('I am a student', 'Я студент'),
            ('I work as a teacher', 'Я работаю учителем'),
            ('Where do you live?', 'Где ты живёшь?'),
            ('I live in Moscow', 'Я живу в Москве'),
            ('What is the weather like?', 'Какая погода?'),
            ('It is sunny', 'Солнечно'),
            ('It is raining', 'Идёт дождь'),
            ('It is cold outside', 'На улице холодно'),
            ('I have a headache', 'У меня болит голова'),
            ('I feel sick', 'Я плохо себя чувствую'),
            ('Take care', 'Береги себя'),
            ('Have a nice day', 'Хорошего дня'),
            ('I agree with you', 'Я согласен с тобой'),
            ('I disagree', 'Я не согласен'),
            ('in my opinion', 'по моему мнению'),
            ('for example', 'например'),
            ('such as', 'такой как'),
            ('more or less', 'более или менее'),
            ('of course', 'конечно'),
            ('by the way', 'кстати'),
            ('in fact', 'на самом деле'),
            ('at least', 'по крайней мере'),
        ],
        'texts': [
            ('Weekend', 'Last weekend I went to the park with my friends. The weather was sunny and warm. We played football and ate ice cream. It was a great day! I love weekends.', 'На прошлых выходных я ходил в парк с друзьями. Погода была солнечная и тёплая. Мы играли в футбол и ели мороженое. Это был отличный день! Я люблю выходные.'),
            ('Shopping', 'Yesterday I went shopping. I bought a new shirt and a pair of shoes. The shirt was cheap, but the shoes were expensive. I am happy with my new clothes. Shopping is fun.', 'Вчера я ходил по магазинам. Я купил новую рубашку и пару обуви. Рубашка была дешёвой, но обувь дорогая. Я доволен новой одеждой. Шопинг это весело.'),
            ('At the Doctor', 'I went to the doctor because I had a headache. The doctor was kind. He gave me medicine. Now I feel much better. I need to sleep more.', 'Я пошёл к врачу, потому что у меня болела голова. Врач был добрым. Он дал мне лекарство. Сейчас я чувствую себя намного лучше. Мне нужно больше спать.'),
        ],
        'pics': [
            'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400',
            'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=400',
            'https://images.unsplash.com/photo-1448630360428-65456659c6df?w=400',
            'https://images.unsplash.com/photo-1534258936925-c58bed479fcb?w=400',
            'https://images.unsplash.com/photo-1506784365847-bbad939e9335?w=400',
        ]
    },
    'B1': {
        'words': [
            ('achievement', 'достижение'), ('advantage', 'преимущество'), ('adventure', 'приключение'),
            ('advertisement', 'реклама'), ('advice', 'совет'), ('ambition', 'амбиция'),
            ('appearance', 'внешность'), ('appointment', 'встреча'), ('attitude', 'отношение'),
            ('audience', 'публика'), ('behaviour', 'поведение'), ('benefit', 'выгода'),
            ('challenge', 'вызов'), ('character', 'характер'), ('charity', 'благотворительность'),
            ('choice', 'выбор'), ('communication', 'общение'), ('community', 'сообщество'),
            ('comparison', 'сравнение'), ('competition', 'соревнование'),
            ('complaint', 'жалоба'), ('confidence', 'уверенность'), ('consequence', 'последствие'),
            ('conversation', 'разговор'), ('courage', 'смелость'), ('culture', 'культура'),
            ('decision', 'решение'), ('development', 'развитие'), ('difference', 'разница'),
            ('disadvantage', 'недостаток'), ('education', 'образование'), ('environment', 'окружающая среда'),
            ('experience', 'опыт'), ('explanation', 'объяснение'), ('expression', 'выражение'),
            ('failure', 'неудача'), ('freedom', 'свобода'), ('friendship', 'дружба'),
            ('government', 'правительство'), ('habit', 'привычка'), ('imagination', 'воображение'),
            ('impression', 'впечатление'), ('independence', 'независимость'),
            ('influence', 'влияние'), ('information', 'информация'), ('knowledge', 'знание'),
            ('leadership', 'лидерство'), ('opportunity', 'возможность'), ('patience', 'терпение'),
            ('performance', 'выступление'), ('permission', 'разрешение'), ('personality', 'личность'),
            ('pollution', 'загрязнение'), ('population', 'население'), ('possibility', 'возможность'),
            ('preparation', 'подготовка'), ('presentation', 'презентация'), ('profession', 'профессия'),
            ('progress', 'прогресс'), ('reality', 'реальность'), ('relationship', 'отношения'),
            ('responsibility', 'ответственность'), ('revolution', 'революция'), ('satisfaction', 'удовлетворение'),
            ('science', 'наука'), ('situation', 'ситуация'), ('society', 'общество'),
            ('solution', 'решение'), ('strength', 'сила'), ('struggle', 'борьба'),
            ('success', 'успех'), ('suggestion', 'предложение'), ('support', 'поддержка'),
            ('technology', 'технология'), ('temperature', 'температура'), ('tradition', 'традиция'),
            ('transport', 'транспорт'), ('university', 'университет'), ('volunteer', 'волонтёр'),
        ],
        'phrases': [
            ('As a result', 'В результате'),
            ('In addition', 'Кроме того'),
            ('On the contrary', 'Наоборот'),
            ('In conclusion', 'В заключение'),
            ('It is worth noting', 'Стоит отметить'),
            ('To be honest', 'Честно говоря'),
            ('As far as I know', 'Насколько я знаю'),
            ('To sum up', 'Подводя итог'),
            ('I am convinced that', 'Я убеждён что'),
            ('It seems to me', 'Мне кажется'),
            ('In other words', 'Другими словами'),
            ('It goes without saying', 'Само собой разумеется'),
            ('To make a long story short', 'Короче говоря'),
            ('Take into account', 'Принять во внимание'),
            ('Pay attention to', 'Обратить внимание на'),
            ('Make a difference', 'Иметь значение'),
            ('Keep in mind', 'Иметь в виду'),
            ('On the one hand', 'С одной стороны'),
            ('On the other hand', 'С другой стороны'),
            ('From my point of view', 'С моей точки зрения'),
        ],
        'texts': [
            ('Technology', 'Technology has changed our lives significantly. People use smartphones for communication, work, and entertainment. However, spending too much time on devices can have negative effects on health and relationships. We should find a balance between online and offline life.', 'Технологии значительно изменили нашу жизнь. Люди используют смартфоны для общения, работы и развлечений. Однако слишком много времени с устройствами может негативно влиять на здоровье и отношения. Мы должны найти баланс между онлайн и офлайн жизнью.'),
            ('Education', 'Education is the key to success. It opens doors to better opportunities and helps people achieve their goals. Many countries invest heavily in education because it is essential for economic development and social progress.', 'Образование — это ключ к успеху. Оно открывает двери к лучшим возможностям и помогает людям достигать своих целей. Многие страны вкладывают значительные средства в образование, потому что оно необходимо для экономического развития и социального прогресса.'),
        ],
        'pics': [
            'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=400',
            'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400',
            'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400',
            'https://images.unsplash.com/photo-1523050854058-8df90910fa58?w=400',
        ]
    },
    'B2': {
        'words': [
            ('abundant', 'обильный'), ('accurate', 'точный'), ('adequate', 'достаточный'),
            ('affordable', 'доступный'), ('ambiguous', 'двусмысленный'),
            ('appropriate', 'подходящий'), ('approximately', 'приблизительно'),
            ('comprehensive', 'всесторонний'), ('considerable', 'значительный'),
            ('consistent', 'последовательный'), ('contemporary', 'современный'),
            ('controversial', 'спорный'), ('crucial', 'решающий'), ('diverse', 'разнообразный'),
            ('efficient', 'эффективный'), ('elaborate', 'разрабатывать'), ('emerge', 'возникать'),
            ('emphasize', 'подчёркивать'), ('enhance', 'усиливать'), ('ensure', 'обеспечивать'),
            ('establish', 'устанавливать'), ('evaluate', 'оценивать'), ('evidence', 'доказательство'),
            ('explicit', 'явный'), ('feasible', 'осуществимый'), ('fluctuate', 'колебаться'),
            ('fundamental', 'фундаментальный'), ('genuine', 'подлинный'), ('gradually', 'постепенно'),
            ('implement', 'осуществлять'), ('imply', 'подразумевать'), ('inevitable', 'неизбежный'),
            ('justify', 'оправдывать'), ('maintain', 'поддерживать'), ('negotiate', 'вести переговоры'),
            ('obstacle', 'препятствие'), ('outcome', 'исход'), ('perspective', 'перспектива'),
            ('precise', 'точный'), ('predominantly', 'преимущественно'), ('preliminary', 'предварительный'),
            ('profound', 'глубокий'), ('reluctant', 'неохотный'), ('resolution', 'решение'),
            ('restrict', 'ограничивать'), ('significant', 'значительный'), ('sufficient', 'достаточный'),
            ('sustainable', 'устойчивый'), ('undergo', 'претерпевать'), ('widespread', 'распространённый'),
        ],
        'phrases': [
            ('As a matter of fact', 'На самом деле'),
            ('By all means', 'Любыми средствами'),
            ('For the time being', 'На данный момент'),
            ('In the long run', 'В долгосрочной перспективе'),
            ('On the whole', 'В целом'),
            ('To a certain extent', 'В определённой степени'),
            ('Under no circumstances', 'Ни при каких обстоятельствах'),
            ('To put it mildly', 'Мягко говоря'),
            ('Without a doubt', 'Без сомнения'),
            ('By and large', 'В общем и целом'),
            ('It is highly likely', 'Весьма вероятно'),
            ('In the light of', 'В свете'),
            ('To be precise', 'Точнее говоря'),
            ('Needless to say', 'Излишне говорить'),
            ('To some extent', 'В некоторой степени'),
        ],
        'texts': [
            ('Climate Change', 'Climate change is one of the most pressing issues of our time. Scientists agree that human activities are responsible for global warming. We must take action to reduce carbon emissions and protect our planet for future generations.', 'Изменение климата — одна из самых острых проблем нашего времени. Учёные согласны, что деятельность человека ответственна за глобальное потепление. Мы должны принять меры по сокращению выбросов углерода и защитить нашу планету для будущих поколений.'),
        ],
        'pics': [
            'https://images.unsplash.com/photo-1507692049790-de58290a4334?w=400',
            'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400',
            'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400',
        ]
    },
    'C1': {
        'words': [
            ('albeit', 'хотя'), ('anecdote', 'анекдот'), ('ascribe', 'приписывать'),
            ('assert', 'утверждать'), ('benevolent', 'доброжелательный'), ('bias', 'предвзятость'),
            ('bizarre', 'странный'), ('coerce', 'принуждать'), ('coherent', 'связный'),
            ('coincide', 'совпадать'), ('comply', 'подчиняться'), ('concise', 'краткий'),
            ('condone', 'потворствовать'), ('conscientious', 'добросовестный'),
            ('contemplate', 'созерцать'), ('criterion', 'критерий'), ('deteriorate', 'ухудшаться'),
            ('devise', 'разрабатывать'), ('dilemma', 'дилемма'), ('diminish', 'уменьшать'),
            ('discrepancy', 'расхождение'), ('disseminate', 'распространять'), ('elicit', 'извлекать'),
            ('elusive', 'неуловимый'), ('endeavor', 'стремление'), ('epitome', 'воплощение'),
            ('exacerbate', 'усугублять'), ('exemplify', 'иллюстрировать'), ('facilitate', 'облегчать'),
            ('fallacy', 'заблуждение'), ('foster', 'способствовать'), ('gregarious', 'общительный'),
            ('hamper', 'препятствовать'), ('hinder', 'мешать'), ('hypothesis', 'гипотеза'),
            ('imminent', 'неизбежный'), ('impartial', 'беспристрастный'), ('incentive', 'стимул'),
            ('indispensable', 'необходимый'), ('infer', 'делать вывод'), ('innate', 'врождённый'),
            ('juxtapose', 'сопоставлять'), ('lenient', 'снисходительный'), ('lucid', 'ясный'),
            ('mundane', 'обыденный'), ('negligent', 'небрежный'), ('notion', 'понятие'),
            ('obsolete', 'устаревший'), ('ominous', 'зловещий'), ('paradigm', 'парадигма'),
            ('plausible', 'правдоподобный'), ('predicament', 'затруднение'), ('prevalent', 'распространённый'),
            ('prolific', 'плодовитый'), ('prudent', 'благоразумный'), ('reiterate', 'повторять'),
            ('scrutiny', 'тщательное изучение'), ('speculate', 'размышлять'), ('substantiate', 'обосновывать'),
            ('trivial', 'незначительный'), ('ubiquitous', 'вездесущий'), ('undermine', 'подрывать'),
            ('unprecedented', 'беспрецедентный'), ('versatile', 'универсальный'), ('vindicate', 'оправдывать'),
            ('volatile', 'изменчивый'), ('warrant', 'оправдывать'), ('zealous', 'рьяный'),
        ],
        'phrases': [
            ('At face value', 'На первый взгляд'),
            ('In conjunction with', 'В сочетании с'),
            ('In stark contrast to', 'В резком контрасте с'),
            ('Bear in mind', 'Иметь в виду'),
            ('Draw a distinction', 'Провести различие'),
            ('In hindsight', 'Задним числом'),
            ('Make a point of', 'Взять за правило'),
            ('On the brink of', 'На грани'),
            ('Out of the question', 'Исключено'),
            ('Put into perspective', 'Взглянуть объективно'),
            ('Strike a balance', 'Найти баланс'),
            ('Take for granted', 'Принимать как должное'),
            ('To say the least', 'Мягко говоря'),
            ('Turn a blind eye', 'Смотреть сквозь пальцы'),
            ('With the exception of', 'За исключением'),
        ],
        'texts': [
            ('Consciousness', 'The concept of consciousness has puzzled philosophers for centuries. While neuroscience has made significant progress, the subjective nature of experience remains elusive. Some argue that consciousness is an emergent property of complex systems.', 'Концепция сознания озадачивала философов веками. Хотя нейронаука добилась значительного прогресса, субъективная природа опыта остаётся неуловимой. Некоторые утверждают, что сознание — это возникающее свойство сложных систем.'),
        ],
        'pics': [
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
            'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400',
            'https://images.unsplash.com/photo-1518281420975-50db6e5d0a97?w=400',
        ]
    }
    
}

def get_level(chat_id):
    return user_levels.get(str(chat_id), 'A1')

def send_message(chat_id, text, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = reply_markup
    requests.post(f'{BASE_URL}/sendMessage', json=payload)

def send_photo(chat_id):
    level = get_level(chat_id)
    pics = WORDS[level]['pics']
    url = random.choice(pics)
    requests.post(f'{BASE_URL}/sendPhoto', json={
        'chat_id': chat_id, 'photo': url,
        'caption': f'🖼 Опиши картинку на английском (уровень {level})'
    })

def send_words(chat_id):
    level = get_level(chat_id)
    words = random.sample(WORDS[level]['words'], min(5, len(WORDS[level]['words'])))
    phrases = random.sample(WORDS[level]['phrases'], min(2, len(WORDS[level]['phrases'])))
    
    text = f"📚 *Уровень {level}*\n\n*Слова:*\n"
    for w in words:
        text += f"• {w[0]} — {w[1]}\n"
    text += "\n*Фразы:*\n"
    for p in phrases:
        text += f"💬 {p[0]} — {p[1]}\n"
    
    keyboard = {'inline_keyboard': [[{'text': '🔄 Ещё', 'callback_data': 'more_words'}]]}
    send_message(chat_id, text, keyboard)

def send_test(chat_id):
    level = get_level(chat_id)
    all_words = WORDS[level]['words']
    
    if len(all_words) < 5:
        send_message(chat_id, 'Мало слов для теста.')
        return
    
    test_words = random.sample(all_words, 5)
    user_test[str(chat_id)] = {'words': test_words, 'index': 0, 'correct': 0}
    send_next_question(chat_id)

def send_next_question(chat_id):
    test = user_test.get(str(chat_id))
    if not test or test['index'] >= 5:
        if test:
            c = test['correct']
            send_message(chat_id, f'🏆 Тест завершён!\n✅ {c}/5\n📈 {c*20}%')
        del user_test[str(chat_id)]
        return
    
    word = test['words'][test['index']]
    level = get_level(chat_id)
    all_words = WORDS[level]['words']
    
    options = [word[1]]
    while len(options) < 4:
        r = random.choice(all_words)[1]
        if r not in options:
            options.append(r)
    random.shuffle(options)
    
    keyboard = {'inline_keyboard': [
        [{'text': opt, 'callback_data': f'quiz_{word[1]}_{opt}'}] for opt in options
    ]}
    send_message(chat_id, f"📝 ({test['index']+1}/5) *{word[0]}*", keyboard)

def send_text(chat_id):
    level = get_level(chat_id)
    text_data = random.choice(WORDS[level]['texts'])
    user_last_text[str(chat_id)] = text_data[2]  # сохраняем перевод
    user_state[str(chat_id)] = 'waiting_translation'
    
    send_message(chat_id, f"📖 *{text_data[0]} (уровень {level})*\n\n{text_data[1]}\n\n✏️ *Переведи этот текст на русский и отправь ответ!*")

def send_dictionary(chat_id):
    send_message(chat_id, '📖 *Словарь*\n\nВведи слово или фразу на *английском* — я переведу.\n\nНапример: `apple`, `hello`, `how are you`')

def search_dictionary(chat_id, query):
    query = query.lower().strip()
    found = []
    
    for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
        # Поиск по словам
        for w in WORDS[level]['words']:
            if len(w) == 3:
                en, ru, cat = w
            else:
                en, ru = w
                cat = ''
            if query == en.lower() or query == ru.lower() or query in en.lower() or query in ru.lower():
                found.append(f'📖 {en} = {ru}' + (f' ({cat})' if cat else '') + f' [уровень {level}]')
        # Поиск по фразам
        for p in WORDS[level]['phrases']:
            en, ru = p
            if query in en.lower() or query in ru.lower():
                found.append(f'💬 {en} = {ru} [уровень {level}]')
        # Поиск по текстам
        for t in WORDS[level]['texts']:
            title, en_text, ru_text = t
            if query in en_text.lower() or query in ru_text.lower():
                found.append(f'📝 {title}: {en_text[:50]}... [{level}]')
    
    if found:
        # Отправляем первые 10 результатов
        send_message(chat_id, '\n\n'.join(found[:10]) + (f'\n\n...и ещё {len(found)-10}' if len(found) > 10 else ''))
    else:
        send_message(chat_id, f'❌ "{query}" не найдено.\nПопробуй другое слово или фразу.')

def process_callback(callback_query):
    chat_id = str(callback_query['message']['chat']['id'])
    data = callback_query['data']
    msg_id = callback_query['message']['message_id']
    
    if data == 'more_words':
        send_words(chat_id)
    elif data.startswith('quiz_'):
        parts = data.split('_')
        correct = parts[1]
        user_answer = parts[2]
        test = user_test.get(chat_id)
        if test:
            if user_answer == correct:
                test['correct'] += 1
                text = '✅ Правильно!'
                add_points(chat_id, 2)
            else:
                text = f'❌ Ответ: {correct}'
            test['index'] += 1
                      requests.post(f'{BASE_URL}/deleteMessage', json={'chat_id': chat_id, 'message_id': msg_id})
            send_message(chat_id, text)
    elif data.startswith('setlevel_'):
        lvl = data.replace('setlevel_', '')
        if lvl in LEVEL_PASSED.get(chat_id, ['A1']):
            user_levels[chat_id] = lvl
        requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': f'✅ Уровень: {lvl}'})
    elif data.startswith('trylevel_'):
        lvl = data.replace('trylevel_', '')
        send_level_test(chat_id, lvl)
        requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': f'Начинаю тест на {lvl}...'})
    elif data.startswith('leveltest_'):
        process_level_test_answer(chat_id, data, msg_id)
    elif data == 'locked':
        requests.post(f'{BASE_URL}/answerCallbackQuery', json={'callback_query_id': callback_query['id'], 'text': '🔒 Уровень закрыт!', 'show_alert': True})
    elif data.startswith('grammar_'):
        topic = data.replace('grammar_', '')
        text = GRAMMAR.get(topic, 'Тема не найдена')
                    requests.post(f'{BASE_URL}/deleteMessage', json={'chat_id': chat_id, 'message_id': msg_id})
            send_message(chat_id, text)
    elif data.startswith('review_show_'):
        card = user_review_cards.get(chat_id)
        if card:
            en, ru = card[0], card[1]
            add_points(chat_id, 1)
            requests.post(f'{BASE_URL}/editMessageText', json={'chat_id': chat_id, 'message_id': msg_id, 'text': f'🔁 {en} = *{ru}*\n\n+1 очко!'})
def process_message(msg):
    chat_id = str(msg['chat']['id'])
    text = msg.get('text', '').strip()
    
    # Инициализация пользователя
    init_user(chat_id)
    
    # Проверка состояния
    if user_state.get(chat_id) == 'waiting_translation':
        user_state[chat_id] = None
        correct = user_last_text.get(chat_id, '')
        add_points(chat_id, 5)
        send_message(chat_id, f'📖 Твой перевод:\n{text}\n\n✅ Пример:\n{correct}\n\n+5 очков!')
        return
    
    if user_state.get(chat_id) == 'waiting_dictation':
        user_state[chat_id] = None
        correct = user_last_text.get(chat_id, '')
        if text.lower().strip() == correct.lower().strip():
            add_points(chat_id, 10)
            send_message(chat_id, f'✅ Правильно! +10 очков!')
        else:
            send_message(chat_id, f'❌ Правильный ответ: {correct}')
        return
    
    # Команды
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
    elif text in ['📖 Словарь', '/dict']:
        send_dictionary(chat_id)
    elif text in ['🎯 Уровень', '/level']:
        send_level_menu(chat_id)
    elif text in ['🎮 Прогресс', '/stats']:
        send_stats(chat_id)
    elif text in ['📝 Грамматика', '/grammar']:
        send_grammar(chat_id)
    elif text in ['🎧 Диктант', '/dictation']:
        send_dictation(chat_id)
    elif text in ['🔁 Повторение', '/repeat']:
        send_review(chat_id)
    elif text in ['🏆 Достижения', '/achievements']:
        send_achievements(chat_id)
    elif text == '❓ Помощь':
        send_message(chat_id, '📚 Слова — изучение\n📝 Тест — 5 вопросов\n📖 Текст — перевод\n🖼 Картинки — описание\n📖 Словарь — поиск\n🎯 Уровень — A1-C1\n🎮 Прогресс — очки\n📝 Грамматика — правила\n🎧 Диктант — аудио\n🔁 Повторение — карточки')
    else:
        search_dictionary(chat_id, text)

# ===== ГЕЙМИФИКАЦИЯ =====
user_points = {}
user_streak = {}
user_last_activity = {}
user_achievements = {}

def init_user(chat_id):
    if chat_id not in user_points:
        user_points[chat_id] = 0
        user_streak[chat_id] = 0
        user_achievements[chat_id] = []

def add_points(chat_id, points):
    init_user(chat_id)
    user_points[chat_id] += points
    check_achievements(chat_id)

def check_achievements(chat_id):
    pts = user_points[chat_id]
    ach = user_achievements[chat_id]
    
    if pts >= 50 and '🎓 Ученик' not in ach:
        ach.append('🎓 Ученик')
        send_message(chat_id, '🏆 Достижение: Ученик! (50 очков)')
    if pts >= 100 and '📚 Знаток' not in ach:
        ach.append('📚 Знаток')
        send_message(chat_id, '🏆 Достижение: Знаток! (100 очков)')
    if pts >= 250 and '🧠 Эксперт' not in ach:
        ach.append('🧠 Эксперт')
        send_message(chat_id, '🏆 Достижение: Эксперт! (250 очков)')
    if pts >= 500 and '👑 Магистр' not in ach:
        ach.append('👑 Магистр')
        send_message(chat_id, '🏆 Достижение: Магистр! (500 очков)')

def send_stats(chat_id):
    init_user(chat_id)
    pts = user_points[chat_id]
    ach = user_achievements[chat_id]
    lvl = get_level(chat_id)
    
    text = f'🎮 *Прогресс*\n\n⭐ Очки: {pts}\n🏆 Достижений: {len(ach)}\n📚 Уровень: {lvl}'
    if ach:
        text += '\n\n🏅 ' + ' | '.join(ach)
    send_message(chat_id, text)

def send_achievements(chat_id):
    init_user(chat_id)
    ach = user_achievements[chat_id]
    if ach:
        send_message(chat_id, '🏆 *Достижения:*\n\n' + '\n'.join(ach))
    else:
        send_message(chat_id, 'Пока нет достижений. Набирай очки!')

# ===== ГРАММАТИКА =====
GRAMMAR = {
    'Present Simple': 'Используется для регулярных действий.\nI work, He works.\nВспомогательный: do/does.\nОтрицание: I don\'t work.',
    'Present Continuous': 'Действие прямо сейчас.\nI am working.\nФормула: am/is/are + V-ing.',
    'Past Simple': 'Действие в прошлом.\nI worked, I went.\nВспомогательный: did.\nОтрицание: I didn\'t go.',
    'Future Simple': 'Действие в будущем.\nI will work.\nОтрицание: I won\'t work.',
    'Articles': 'a/an — неопределённый.\nthe — определённый.\nNo article — общее понятие.',
    'Modal Verbs': 'can — могу, должен.\nshould — следует.\nmust — обязан.\nmay — можно.',
}

def send_grammar(chat_id):
    topics = list(GRAMMAR.keys())
    keyboard = {'inline_keyboard': [
        [{'text': t, 'callback_data': f'grammar_{t}'}] for t in topics
    ]}
    send_message(chat_id, '📝 *Грамматика*\nВыбери тему:', keyboard)

# ===== ДИКТАНТ =====

def send_dictation(chat_id):
    level = get_level(chat_id)
    items = WORDS[level]['words'] + WORDS[level]['phrases']
    if not items: return
    
    item = random.choice(items)
    en = item[0]
    user_last_text[chat_id] = en
    user_state[chat_id] = 'waiting_dictation'
    
    # Google Translate TTS — бесплатно и без API-ключа
    tts_url = f'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q={requests.utils.quote(en)}'
    
    try:
        response = requests.get(tts_url)
        if response.status_code == 200:
            # Отправляем как голосовое
            files = {'voice': ('audio.mp3', response.content, 'audio/mpeg')}
            requests.post(f'{BASE_URL}/sendVoice', files=files, data={'chat_id': chat_id, 'caption': '🎧 Напиши перевод!'})
        else:
            send_message(chat_id, f'🎧 *Диктант*\nНапиши: _{en}_')
    except:
        send_message(chat_id, f'🎧 *Диктант*\nНапиши: _{en}_')

# ===== ИНТЕРВАЛЬНЫЕ ПОВТОРЕНИЯ =====
user_review_cards = {}

def send_review(chat_id):
    level = get_level(chat_id)
    words = WORDS[level]['words']
    if len(words) < 4:
        send_message(chat_id, 'Мало слов для повторения.')
        return
    
    card = random.choice(words)
    user_review_cards[chat_id] = card
    en, ru = card[0], card[1]
    
    keyboard = {'inline_keyboard': [[
        {'text': 'Показать перевод', 'callback_data': f'review_show_{chat_id}'}
    ]]}
    send_message(chat_id, f'🔁 *Повторение*\n\nСлово: *{en}*\n\nВспомни перевод и нажми кнопку.', keyboard)
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
# ===== НАПОМИНАНИЯ =====
def check_reminders():
    """Вызывается раз в час через внешний сервис (cron-job.org)"""
    for chat_id in user_points.keys():
        send_message(chat_id, '⏰ Не забудь позаниматься английским! 📚')

def send_menu(chat_id):
    keyboard = {
        'keyboard': [
            [{'text': '📚 Слова'}, {'text': '📝 Тест'}],
            [{'text': '📖 Текст'}, {'text': '🖼 Картинки'}],
            [{'text': '📖 Словарь'}, {'text': '🎯 Уровень'}],
            [{'text': '🎮 Прогресс'}, {'text': '📝 Грамматика'}],
            [{'text': '🎧 Диктант'}, {'text': '🔁 Повторение'}],
            [{'text': '🏆 Достижения'}, {'text': '❓ Помощь'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, '📍 Меню:', keyboard)


# ===== СИСТЕМА УРОВНЕЙ =====
LEVEL_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1']
LEVEL_TESTS = {}
LEVEL_PASSED = {}

def send_level_test(chat_id, level):
    # Тест по словам ТЕКУЩЕГО уровня, чтобы перейти на следующий
    current_level = get_level(chat_id)
    words = WORDS[current_level]['words']
    if len(words) < 10:
        send_message(chat_id, 'Недостаточно слов для теста.')
        return
    test_words = random.sample(words, 10)
    LEVEL_TESTS[chat_id] = {'level': level, 'words': test_words, 'index': 0, 'correct': 0}
    send_level_question(chat_id)

def send_level_question(chat_id):
    test = LEVEL_TESTS.get(chat_id)
    if not test:
        return
    if test['index'] >= 10:
        correct = test['correct']
        level = test['level']
        if correct >= 8:
            if level not in LEVEL_PASSED.get(chat_id, []):
                LEVEL_PASSED.setdefault(chat_id, ['A1']).append(level)
            user_levels[chat_id] = level
            send_message(chat_id, f'🎉 Уровень {level} пройден! ✅ {correct}/10')
        else:
            send_message(chat_id, f'😔 Не сдал. {correct}/10. Нужно 8/10.')
        del LEVEL_TESTS[chat_id]
        return
    word = test['words'][test['index']]
    all_words = WORDS[test['level']]['words']
    options = [word[1]]
    while len(options) < 4:
        r = random.choice(all_words)[1]
        if r not in options:
            options.append(r)
    random.shuffle(options)
    keyboard = {'inline_keyboard': [[{'text': opt, 'callback_data': f'leveltest_{word[1]}_{opt}'}] for opt in options]}
    send_message(chat_id, f"📝 Уровень {test['level']} ({test['index']+1}/10)\n*{word[0]}*", keyboard)

def process_level_test_answer(chat_id, data, msg_id):
    parts = data.split('_')
    correct = parts[1]
    user_answer = parts[2]
    test = LEVEL_TESTS.get(chat_id)
    if not test:
        return
    if user_answer == correct:
        test['correct'] += 1
        text = '✅'
    else:
        text = f'❌ {correct}'
    test['index'] += 1
    
    # Удаляем сообщение с вопросом
    requests.post(f'{BASE_URL}/deleteMessage', json={'chat_id': chat_id, 'message_id': msg_id})
    
    # Отправляем результат и следующий вопрос
    send_message(chat_id, text)
    send_level_question(chat_id)
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
