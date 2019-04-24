from flask import Flask, request
import urllib.request
import requests
import logging
import json
from translate import translate
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')
answers = {"solid": "Это аббревиатура, которая обозначает 5 принципов:\n"
                    "Single responsibility,"
                    "Open сlosed,"
                    "Liskov Substitution,"
                    "Interface Segregation,"
                    "Dependency Inversion.",
           "single responsibility": "Каждый объект выполняет лишь одну задачу",
           "open сlosed": "Программные сущности должны быть открыты для расширения, но закрыты для изменения",
           "liskov substitution": "Наследующий класс должен дополнять, а не изменять базовый",
           "interface segregation": "Много интерфейсов, специально предназначенных для клиентов, лучше, "
                                    "чем один интерфейс общего назначения",
           "dependency inversion": "Зависимость на Абстракциях. Нет зависимости на что-то конкретное.",
           "функция вывода в консоль": "print()",
           "функция ввода данных в консоль": "input()",
           "функция модуль": "abs()"
           }

python_answers = {
    "когда": "Язык программирования Python появился 20 февраля 1991 года",
    "сколько лет": "В 2019 году языку Python исполнилось 28 лет",
    "кто создал": "Язык Питон был создан Гвидо ван Россумом.",
    "имя создателя": "Гвидо ван Россум",
    "имя автора": "Гвидо ван Россум",
    "название": "Гвидо ван Россум, был поклонником Британского комедийного шоу «Летающий цирк Монти Пайтона»."
                "Вот и в честь «Монти Пайтона (Monty Python)» язык назвался Python.",
    "дзен": "Чтобы увидеть дзен языка питон, впишите команду 'import this'"
}

already_shown = []
memes = [i for i in range(1, 2141)]

@app.route('/post', methods=['POST'])
def main():

    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):
    res['response']['text'] = ""

    res['response']['buttons'] = [
        {
            'title': 'Django for girls',
            "url": "https://tutorial.djangogirls.org/ru/",
            'hide': True
        },
        {
            'title': 'PyGame',
            "url": "https://www.pygame.org/docs/",
            'hide': True
        },
        {
            'title': 'StackOverFlow',
            "url": "https://ru.stackoverflow.com/",
            'hide': True
        },
        {
            'title': 'Карта Яндекс Лицеев',
            "url": "https://yandex.ru/maps/-/CCRu5Nn6",
            'hide': True
        },
        {
            'title': 'import antigravity',
            "url": "https://xkcd.com/353/",
            'hide': True
        }

    ]
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я Алиса.' \
                ' Я могу рассказать вам про язык Python и принципы программирования, a также открыть сайты библиотек.'
        return

    if req['request']["command"] in ["PyGame", "StackOverFlow",
                                     "Карта Яндекс Лицеев", "Django for girls", "import antigravity"]:
        res['response']['text'] = "Вот ваша страница"
        return
    command = req['request']["command"].lower()

    if "покажи" in command and "мем" in command:
        if len(memes) != len(already_shown):
            meme = random.choice(memes)
            while meme in already_shown:
                meme = random.choice(memes)
            url = urllib.request.urlopen(f"https://xkcd.com/{meme}/info.0.json")
            m = json.loads(url.read().decode())
            image = m["img"]

            r = requests.post("https://dialogs.yandex.net/api/v1/skills/6309f400-2e62-41c9-9879-31054a05465a/images",
                              headers={"Authorization": "OAuth AQAAAAAgUp_wAAT7o0KUof8Hr0KBjmZ59Harjk4",
                                       "Content-Type": "application/json"},
                              json={"url": image})
            data = json.loads(r.content)
            res['response']['card'] = {}
            res['response']['text'] = " "
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Вот мем'
            res['response']['card']['image_id'] = data["image"]["id"]
            already_shown.append(meme)
            return
        res['response']['text'] = "У меня закочились мемы :("
        return

    text = get_text(command)
    if text is not None:
        text = translate(text, "ru")
        if text != "eter: tex":
            res['response']['text'] = text
        else:
            res['response']['text'] = 'Я не расслышала слово для перевода. Повторите пожалуйста'
        return

    for key in answers.keys():
        if key in command:
            res['response']['text'] = answers[key]
            return

    if "python" in command or \
       "питон" in command:
        for key in python_answers.keys():
            if key in req['request']["command"].lower():
                res['response']['text'] = python_answers[key]
                break
        else:
            res['response']['text'] = "Питон - это высокоуровневый язык программирования общего назначения, " \
                                      "ориентированный наповышение производительности разработчика и читаемости кода."
        return

    if req['response']['text'] == "" and req['request']['command'] != "Ваш запрос":
        res['response']['text'] = "Всё найдется в Яндексе!"
        search = req['request']['command'].replace(" ", "+")
        url = f"https://yandex.ru/search/?lr=75&text={search}"
        res['response']['buttons'] = [
            {
                'title': 'Ваш запрос',
                "url": url,
                'hide': False
            }
        ]
        return
    res['response']['text'] = 'Вот ваш запрос'


def get_text(command):
    command = command.split()
    text = None
    commands = ["переведи фразу", "переведите фразу", "переведи слово", "переведите слово"]
    for i in commands:
        if i in " ".join(command):
            text = " ".join(command[2:])
    return text


if __name__ == '__main__':
    app.run()
