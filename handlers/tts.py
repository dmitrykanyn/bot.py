# telegram_bot/handlers/tts.py

import openai
import logging
from pathlib import Path

# Настройка логирования
logger = logging.getLogger(__name__)

# Установите ваш API-ключ OpenAI
openai.api_key = "sk-proj-sdYTeYNI6Wcz9jPc3JunT3BlbkFJL6LKvOEYM6eK5xx8csPk"

def text_to_speech(text, file_path):
    try:
        response = openai.Audio.create(
            model="text-to-speech-1",
            input=text,
            voice="alloy"
        )

        audio_data = response['data'][0]['audio']
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        return file_path
    except Exception as e:
        logger.error(f"Ошибка при преобразовании текста в голос: {e}")
        return None
