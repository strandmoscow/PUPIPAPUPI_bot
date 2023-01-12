import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

import inequality.inequality as inequality

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    str = "Привет/Шалом/Салам/Барэв дзэс/Хэллоу\nЯ что-то умею! Смотри список команд или тыкай /help"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Смотри, что есть в этом боте:\n",
        "\\inequality - посчитать неравенство из задания."
    )


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5870746171:AAEVBVeUmVOfX03V24kdWO7fViT128xEr6U").build()

    # Add handler
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    inequality_handler = inequality.inequality_handler

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(inequality_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
