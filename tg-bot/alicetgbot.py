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
    FEED_ADD = 5
    FEED_DELETE = 6


class AliceTelegramBot:
    def __init__(self, token: str):
        self.updater = Updater(token, use_context=True)

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self._logger = logging.getLogger(__name__)

        self.api = API(os.getenv('API_HOST'))

        self.debug = True

    def start(self):
        dp = self.updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.cmd_start)],

            states={
                Code.BEFORE_AUTH:          [MessageHandler(Filters.text, self.before_auth)],
                Code.CODE_ENTER:           [MessageHandler(Filters.text, self.code_enter)],
                Code.CODE_ALICE_APPROVING: [MessageHandler(Filters.text, self.code_alice_approving)],
                Code.MENU:                 [MessageHandler(Filters.text, self.menu)],
                Code.FEED_ADD:             [MessageHandler(Filters.text, self.menu)],
                Code.FEED_DELETE:          [MessageHandler(Filters.text, self.menu)],
            },

            fallbacks=[]
        )
        dp.add_handler(conv_handler)

    def run(self):
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
        if not self.debug and ((not code.isdigit()) or len(code) != 6):
            update.message.reply_text(Messages.code_invalid)
            return

        update.message.reply_text(Messages.code_checking)

        received_from = f'{update.message.from_user.first_name}'
        if update.message.from_user.last_name:
            received_from += f' {update.message.from_user.last_name}'
        if update.message.from_user.username:
            received_from += f', юзернейм {update.message.from_user.username}'

        api_message = self.api.code_confirm(code=str(code), bot_type='Telegram', bot_user_id=update.message.from_user.id,
                                            received_from=received_from)
        update.message.reply_text(api_message)

        if api_message == Messages.api_code_confirm_success or (self.debug and code == '-1'):
            update.message.reply_text(Messages.code_valid, reply_markup=ReplyKeyboardMarkup([[UserReplies.code_alice_approved],
                                                                                             [UserReplies.code_alice_new]]))
            return Code.CODE_ALICE_APPROVING
        else:
            update.message.reply_text(Messages.code_invalid)

    def code_alice_approving(self, update: Update, context: CallbackContext):
        if update.message.text == UserReplies.code_alice_new:
            update.message.reply_text(Messages.code_entry, reply_markup=ReplyKeyboardRemove())
            return Code.CODE_ENTER

        update.message.reply_text(Messages.code_alice_checking)
        api_data = self.api.get_user_by_telegram_id(update.message.from_user.id)

        if isinstance(api_data, dict) or (self.debug and update.message.text == 'y'):
            update.message.reply_text(Messages.code_alice_ok, reply_markup=ReplyKeyboardMarkup(UserReplies.menu_channel_keyboard))
            update.message.reply_text(Messages.help)
            return Code.MENU
        elif isinstance(api_data, str) or (self.debug and update.message.text == 'n'):
            update.message.reply_text(api_data)
            update.message.reply_text(Messages.code_alice_error)

    def menu(self, update: Update, context: CallbackContext):
        self.log(update)

        msg = update.message.text
        if msg == UserReplies.menu_channel_list:
            update.message.reply_text(Messages.menu_channel_list)
            api_response = self.api.get_tg_feed(update.message.from_user.id)

            if isinstance(api_response, str):
                update.message.reply_text(api_response)
            else:
                update.message.reply_text('\n'.join(f'{x[0]}. {x[1]}, {x[2]}' for x in api_response['feed']))

        elif msg == UserReplies.menu_channel_add:
            update.message.reply_text(Messages.menu_channel_add, reply_markup=ReplyKeyboardMarkup([[UserReplies.back_to_menu]]))
            return Code.FEED_ADD

        elif msg == UserReplies.menu_channel_delete:
            update.message.reply_text(Messages.menu_channel_delete, reply_markup=ReplyKeyboardMarkup([[UserReplies.back_to_menu]]))
            return Code.FEED_DELETE

        else:
            update.message.reply_text(Messages.menu_use_kb)

    def feed_add(self, update: Update, context: CallbackContext):
        text = update.message.text

        if text == UserReplies.back_to_menu:
            update.message.reply_text(Messages.back_to_menu, reply_markup=ReplyKeyboardMarkup(UserReplies.menu_channel_keyboard))
            return Code.MENU

        try:
            name, url = update.message.text.split()[:-1], update.message.text.split()[-1]
        except Exception as e:
            update.message.reply_text(Messages.feed_add_invalid)
            return

        api_response = self.api.add_tg_feed(update.message.from_user.id, name, url)
        if isinstance(api_response, str):
            update.message.reply_text(api_response)
        else:
            update.message.reply_text(Messages.feed_add_success.format(api_response['id']))

    def feed_delete(self, update: Update, context: CallbackContext):
        text = update.message.text

        if text == UserReplies.back_to_menu:
            update.message.reply_text(Messages.back_to_menu, reply_markup=ReplyKeyboardMarkup(UserReplies.menu_channel_keyboard))
            return Code.MENU

        try:
            tape_id = int(text)
        except Exception as e:
            update.message.reply_text(Messages.feed_delete_invalid)
            return

        api_response = self.api.delete_tg_feed(update.message.from_user.id, tape_id)
        if isinstance(api_response, str):
            update.message.reply_text(api_response)
        else:
            update.message.reply_text(Messages.feed_delete_success.format(tape_id))

    def log(self, update: Update):
        self._logger.info(f'Message from {update.message.from_user.first_name} = {update.message.text}')


if __name__ == '__main__':
    dotenv.load_dotenv('../.env')
    bot = AliceTelegramBot(os.getenv('TELEGRAM_BOT_TOKEN'))
    bot.start()

    USERS_DATA = [
        (Code.MENU, 436053437)
    ]

    for state, tg_id in USERS_DATA:
        bot.updater.dispatcher.handlers[0][0].update_state(state, (tg_id, tg_id))

    bot.run()
