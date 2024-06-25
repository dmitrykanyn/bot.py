import logging
import os
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from .generate import generate_dalle_image  # Импорт функции для генерации фото

# Настройка логирования
logger = logging.getLogger(__name__)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.message.from_user.id
        photo_file = await update.message.photo[-1].get_file()
        photo_path = f"user_{user_id}_photo.jpg"
        await photo_file.download(photo_path)

        context.user_data["photo_path"] = photo_path
        await update.message.reply_text(f"Фото сохранено как {photo_path}")
        logger.info(f"Фото пользователя {user_id} сохранено как {photo_path}")
    except Exception as e:
        logger.error(f"Ошибка при обработке фотографии: {e}")
        await update.message.reply_text("Произошла ошибка при обработке фотографии. Пожалуйста, попробуйте позже.")
