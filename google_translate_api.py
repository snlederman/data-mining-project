from googletrans import Translator

TARGET = "en"


def translate_text(text):
    """Translates text into the target language.
    """
    translator = Translator()
    translation = translator.translate(text, dest=TARGET)
    print(translation.text)

translate_text('Hola mundo')
