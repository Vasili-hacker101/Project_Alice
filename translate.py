import requests


def translate(text, lang):

    url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    params = {
        'key': 'trnsl.1.1.20190418T090543Z.d4240053a810d6e4.a44e1e6b6ec76310c9692bab6e41fb6c35e4d2f6',
        'text': text,
        'lang': lang
    }

    response = requests.get(url, params).text
    rus_text = response[36:(len(response)-3)]
    return rus_text
