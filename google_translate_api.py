import os
import six
from google.cloud import translate_v2 as translate

import requests
r = requests.get('https://translation.googleapis.com/language/translate/v2', headers='data-371303-48c6a5a1041f.json')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'data-371303-48c6a5a1041f.json'
TARGET = 'en'

def translate_text(text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=TARGET)

    print(format(result["translatedText"]))
