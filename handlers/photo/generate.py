import openai
import logging
import requests

# Настройка логирования
logger = logging.getLogger(__name__)

# Установите ваш API-ключ OpenAI
openai.api_key = "sk-proj-sdYTeYNI6Wcz9jPc3JunT3BlbkFJL6LKvOEYM6eK5xx8csPk"  # Замените на ваш API-ключ

async def generate_dalle_image(prompt):
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        image_url = response['data'][0]['url']
        image_data = requests.get(image_url).content
        return image_data
    except Exception as e:
        logger.error(f"Ошибка при генерации изображения: {e}")
        return None
