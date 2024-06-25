import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.handlers import handle_message, handle_photo, handle_audio
from handlers.commands.commands import start, stop_generation, help_command  # Импорт команд

# Настройка логирования для записи в файл и вывода в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/telegram-bot/telegram_bot/logs/bot.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        if update and update.message:
            await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
        elif update and update.callback_query:
            await update.callback_query.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
        else:
            logger.error("Update is None or Update without message: %s", update)
    except Exception as e:
        logger.error(f"Ошибка в обработчике ошибок: {e}")

def main() -> None:
    # Вставьте ваш токен Telegram бота
    token = "7281346810:AAG748dFdw-SdkyK2z1KRnM_cIFy1LoZmM4"
    
    # Создание приложения Telegram
    application = Application.builder().token(token).build()

    # Добавление обработчиков команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_generation))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    
    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    logger.info("Запуск бота...")
    application.run_polling()

if __name__ == "__main__":
    main()
