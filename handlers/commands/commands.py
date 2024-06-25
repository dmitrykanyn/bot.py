# telegram_bot/handlers/commands/commands.py

from telegram import Update
from telegram.ext import ContextTypes

# Обработчик для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['active'] = True
    context.user_data['stop'] = False
    await update.message.reply_text("Привет! Какой у тебя вопрос?")

# Обработчик для команды /stop
async def stop_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['stop'] = True
    if 'task' in context.user_data and context.user_data['task']:
        context.user_data['task'].cancel()
        context.user_data['task'] = None
    await update.message.reply_text("Генерация текущего ответа остановлена.")

# Обработчик для команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start - Начать работу с ботом\n"
        "/stop - Остановить генерацию ответа\n"
        "/help - Получить список команд"
    )
