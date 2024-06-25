import openai
import logging
import asyncio
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from .tts import text_to_speech
from .utils import ask_openai_stream
from .audio import transcribe_audio
from .photo.handle import handle_photo
from .photo.generate import generate_dalle_image
from .commands.commands import start, stop_generation, help_command
# from .user_data.history import save_user_history, load_user_history  # Удаляем импорт функций для сохранения и загрузки истории

# Установите ваш API-ключ OpenAI
openai.api_key = "sk-proj-sdYTeYNI6Wcz9jPc3JunT3BlbkFJL6LKvOEYM6eK5xx8csPk"

# Настройка логирования
logger = logging.getLogger(__name__)

# Обработчик для текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_question = update.message.text.lower()

    # Загружаем историю пользователя
    # context.user_data["conversation_history"] = load_user_history(user_id)
    context.user_data["conversation_history"] = []
    context.user_data["conversation_history"].insert(0, {"role": "system", "content": "Business Assistant helps users solve various business problems by providing intelligent and effective solutions. With intelligent humor, he makes interactions pleasant and easy. Also uses a random number of emoticons in the text, but no more than 5 per message. The assistant analyzes information, provides recommendations and helps in planning and organizing business processes. Its goal is to make it easier for users to complete tasks и make informed decisions."})

    if user_question == "стоп":
        await stop_generation(update, context)
    elif "запомни" in user_question:
        text_to_remember = user_question.replace("запомни", "").strip()
        if text_to_remember:
            # save_user_history(user_id, text_to_remember)
            await update.message.reply_text("Я запомнил это!")
        else:
            await update.message.reply_text("Пожалуйста, укажите текст для запоминания.")
    elif any(phrase in user_question for phrase in ["сгенерируй изображение", "создай фото", "создай изображение"]):
        prompt = user_question.split(maxsplit=1)[1] if len(user_question.split(maxsplit=1)) > 1 else ""
        await update.message.reply_text("Генерация изображения, пожалуйста подождите...")
        image_data = await generate_dalle_image(prompt)
        if image_data:
            await update.message.reply_photo(photo=InputFile(image_data, filename="image.png"))
        else:
            await update.message.reply_text("Произошла ошибка при генерации изображения.")
    elif "отправь мою фотографию" in user_question:
        photo_path = context.user_data.get("photo_path")
        if photo_path and os.path.exists(photo_path):
            await update.message.reply_photo(photo=InputFile(photo_path))
        else:
            await update.message.reply_text("У меня нет сохраненных фотографий для отправки.")
    elif user_question.startswith("сделай голосовое сообщение"):
        text = user_question.replace("сделай голосовое сообщение", "").strip()
        if text:
            speech_file_path = Path(__file__).parent / f"{user_id}_speech.mp3"
            await update.message.reply_text("Преобразование текста в голос, пожалуйста подождите...")
            speech_file = await asyncio.to_thread(text_to_speech, text, speech_file_path)
            if speech_file:
                await update.message.reply_audio(audio=open(speech_file, "rb"))
            else:
                await update.message.reply_text("Произошла ошибка при преобразовании текста в голос.")
        else:
            await update.message.reply_text("Пожалуйста, предоставьте текст для преобразования в голос.")
    else:
        if context.user_data.get('active', True):
            if 'task' in context.user_data and context.user_data['task']:
                context.user_data['task'].cancel()
            context.user_data['task'] = asyncio.create_task(ask_openai_stream(user_question, update, context))
            # Сохраняем вопрос пользователя в истории
            context.user_data.setdefault("conversation_history", []).append(
                {"role": "user", "content": user_question}
            )
            # save_user_history(user_id, context.user_data["conversation_history"])
        else:
            await update.message.reply_text("Бот остановлен. Используйте команду /start для перезапуска.")

# Обработчик для аудио сообщений
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await transcribe_audio(update, context)
