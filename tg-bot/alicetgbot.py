import logging
import os

import dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

from message_strings import Messages, UserReplies
from api import API


class Code:
    BEFORE_AUTH = 1
    CODE_ENTER = 2
    CODE_ALICE_APPROVING = 3
    MENU = 4


class AliceTelegramBot:
    def __init__(self, token: str):
        self.updater = Updater(token, use_context=True)

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self._logger = logging.getLogger(__name__)

        self.api = API(os.getenv('API_HOST'))

    def start(self):
        dp = self.updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.cmd_start)],

            states={
                Code.BEFORE_AUTH:          [MessageHandler(Filters.text, self.before_auth)],
                Code.CODE_ENTER:           [MessageHandler(Filters.text, self.code_enter)],
                Code.CODE_ALICE_APPROVING: [MessageHandler(Filters.text, self.code_alice_approving)],
                Code.MENU:                 [MessageHandler(Filters.text, self.menu)],
            },

            fallbacks=[]
        )

        dp.add_handler(conv_handler)

        self.updater.start_polling()
        self.updater.idle()

    def cmd_start(self, update: Update, context: CallbackContext):
        self.log(update)

        reply_keyboard = [[UserReplies.enter_code]]
        update.message.reply_text(Messages.cmd_start,
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard))
        return Code.BEFORE_AUTH

    def before_auth(self, update: Update, context: CallbackContext):
        self.log(update)
        if update.message.text == UserReplies.enter_code:
            update.message.reply_text(Messages.code_entry, reply_markup=ReplyKeyboardRemove())
            return Code.CODE_ENTER
        else:
            update.message.reply_text(Messages.code_auth_first)

    def code_enter(self, update: Update, context: CallbackContext):
        self.log(update)

        code = str(update.message.text).strip()
        if len(code) != 6:
            code += 'ValueError'

        try:
            code = int(code)
        except ValueError:
            update.message.reply_text(Messages.code_invalid)
            return

        update.message.reply_text(Messages.code_checking)
        api_message = self.api.code_confirm(code=str(code), bot_type='Telegram', bot_user_id=update.message.from_user.id,
                                            received_from=f'{update.message.from_user.first_name}')
        update.message.reply_text(api_message)

        if api_message == Messages.api_code_confirm_success:
            update.message.reply_text(Messages.code_valid, reply_markup=ReplyKeyboardMarkup([[UserReplies.code_alice_approved]]))
            return Code.CODE_ALICE_APPROVING
        else:
            update.message.reply_text(Messages.code_invalid)

    def code_alice_approving(self, update: Update, context: CallbackContext):
        update.message.reply_text(Messages.code_alice_checking)
        api_data = self.api.get_user_by_telegram_id(update.message.from_user.id)

        if isinstance(api_data, str):
            update.message.reply_text(api_data)
            update.message.reply_text(Messages.code_alice_error)
        else:
            update.message.reply_text(Messages.code_alice_ok, reply_markup=ReplyKeyboardRemove())
            update.message.reply_text(Messages.help)
            return Code.MENU

    def menu(self, update: Update, context: CallbackContext):
        self.log(update)
        update.message.reply_text('Menu')

    def log(self, update: Update):
        self._logger.info(f'Message from {update.message.from_user.first_name} = {update.message.text}')


if __name__ == '__main__':
    dotenv.load_dotenv('../.env')
    bot = AliceTelegramBot(os.getenv('TELEGRAM_BOT_TOKEN'))
    bot.start()
