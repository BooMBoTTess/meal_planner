import logging

from telegram_controller import controller
import main

logger = logging.getLogger('bot')
main.start()
controller.bot.infinity_polling()  # type: ignore