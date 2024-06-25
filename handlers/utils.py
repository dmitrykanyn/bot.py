import openai
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

# Настройка логирования
logger = logging.getLogger(__name__)

# Установите ваш API-ключ OpenAI
openai.api_key = "sk-proj-sdYTeYNI6Wcz9jPc3JunT3BlbkFJL6LKvOEYM6eK5xx8csPk"

def ensure_message_format(message):
    """Преобразует сообщение в правильный формат, если оно не является объектом с ключами 'role' и 'content'."""
    if isinstance(message, list):
        return [ensure_message_format(m) for m in message]
    if isinstance(message, str):
        return {"role": "user", "content": message}
    if isinstance(message, dict) and 'role' in message and 'content' in message:
        return message
    logger.error(f"Invalid message format: {message}")
    return None

async def ask_openai_stream(user_question, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.message.from_user.id
        user_history = context.user_data.get("conversation_history", [])

        # Проверка и преобразование формата сообщений
        user_history = [ensure_message_format(msg) for msg in user_history if ensure_message_format(msg) is not None]

        # Проверка и преобразование текущего сообщения
        user_question = ensure_message_format(user_question)
        if user_question is None:
            logger.error(f"Invalid user question format: {user_question}")
            await update.message.reply_text("Invalid message format.")
            return

        message = await update.message.reply_text("Генерация ответа...")
        response_text = ""
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=user_history + [user_question],
            stream=True
        )
        chunk_text = ""
        async for chunk in response:
            if context.user_data.get('stop', False):
                await message.edit_text("Генерация остановлена.")
                return
            delta = chunk.choices[0].delta.get('content', '')
            if delta:
                chunk_text += delta
                if len(chunk_text) >= 100:  # Обновление каждые 100 символов
                    response_text += chunk_text
                    try:
                        if response_text != message.text:
                            await message.edit_text(response_text)
                        await asyncio.sleep(0.1)  # Минимальная задержка между запросами для предотвращения Flood control
                        chunk_text = ""
                    except Exception as e:
                        logger.error(f"Ошибка при редактировании сообщения: {e}")
                        if "Flood control exceeded" in str(e):
                            retry_after = int(str(e).split("Retry in ")[1].split(" ")[0])
                            await asyncio.sleep(retry_after)
                        elif "Timed out" in str(e):
                            await asyncio.sleep(5)
                        else:
                            break
        response_text += chunk_text
        if response_text != message.text:
            await message.edit_text(response_text)
        # Сохраняем историю сообщений
        context.user_data.setdefault("conversation_history", []).append(
            {"role": "assistant", "content": response_text}
        )
    except asyncio.CancelledError:
        return
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса. Попробуйте позже.")
