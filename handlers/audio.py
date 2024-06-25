import openai
import logging
from telegram import Update, File
from telegram.ext import ContextTypes
import tempfile
from pydub import AudioSegment
from .utils import ask_openai_stream  # Импортируем только ask_openai_stream из utils.py

# Настройка логирования
logger = logging.getLogger(__name__)

# Установите ваш API-ключ OpenAI
openai.api_key = "sk-proj-sdYTeYNI6Wcz9jPc3JunT3BlbkFJL6LKvOEYM6eK5xx8csPk"

async def transcribe_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Получаем файл аудио из сообщения
        audio_file: File = await update.message.voice.get_file()

        with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
            original_audio_path = temp_audio_file.name
            await audio_file.download_to_drive(original_audio_path)

        # Преобразование аудио в поддерживаемый формат (например, wav)
        audio = AudioSegment.from_file(original_audio_path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
            wav_audio_path = temp_wav_file.name
            audio.export(wav_audio_path, format="wav")

        # Распознавание аудио с помощью OpenAI
        with open(wav_audio_path, 'rb') as audio:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio
            )

        # Отправка расшифровки пользователю
        transcript = response['text']
        if "транскрибируй" in transcript.lower():
            await update.message.reply_text(f"Расшифровка: {transcript}")
        else:
            context.user_data.setdefault("conversation_history", []).append(
                {"role": "user", "content": transcript}
            )
            await ask_openai_stream(transcript, update, context)

    except Exception as e:
        logger.error(f"Ошибка при распознавании аудио: {e}")
        await update.message.reply_text("Произошла ошибка при распознавании аудио. Пожалуйста, попробуйте позже.")
