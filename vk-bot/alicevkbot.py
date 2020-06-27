import configparser
import logging
import os
import sys
import threading
import time
import traceback

import dotenv

import bot_messages as msg
from vkasyncbot import VkBot
from vkasyncbot.ext import DialogData
from vkasyncbot.obj import ButtonText, ButtonTextColor, CarouselElement, Keyboard, Message
from api import API
from message_strings import Messages, UserReplies

dotenv.load_dotenv('../.env')

DB_JSON = 'db.json'
LOG_PATH = 'logs/'
ADMIN_ONLY = 1

DEBUG = True

config = configparser.ConfigParser()
config.read('config.ini')

group_id = int(os.getenv('VK_BOT_GROUP_ID'))
# admin_id = int(os.getenv('VK_BOT_ADMIN_ID'))
admin_id = 223712375
access_token = os.getenv('VK_BOT_ACCESS_TOKEN')
secret_key = os.getenv('VK_BOT_SECREY_KEY')

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] - %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S',
                    stream=sys.stdout,
                    # filename=f'{LOG_PATH}/wallbot.log',
                    level=logging.INFO)

bot = VkBot(group_id, access_token, secret_key)
bot.load_json_db(DB_JSON)
bot.set_permissions([(admin_id, 99999)])

api = API(os.getenv('API_HOST'))


def delayed_exit(sec: int):
    logging.info('Shutdown command received!')
    for i in range(sec, 0, -1):
        logging.info(f'Shutting down in {i}...')
        time.sleep(1)
    logging.info('Running os._exit(0)...')
    os._exit(0)


@bot.message('/')
async def root(dialog: DialogData):
    await dialog.reply(Messages.cmd_start, Keyboard([[ButtonText(UserReplies.enter_code)]]))
    dialog.user.change_page('/before-auth')


@bot.message('/before-auth')
async def root(dialog: DialogData):
    if dialog.msg.text == UserReplies.enter_code:
        await dialog.reply(Messages.code_entry, Keyboard(empty=True))
        dialog.user.change_page('/code-enter')
    else:
        await dialog.reply(Messages.code_auth_first)


@bot.message('/code-enter')
async def code_enter(dialog: DialogData):
    code = str(dialog.msg.text).strip().replace(' ', '').replace('\t', '')
    if not DEBUG and ((not code.isdigit()) or len(code) != 6):
        await dialog.reply(Messages.code_invalid)
        return

    await dialog.reply(Messages.code_checking)

    received_from = f'Айди Вконтакте {dialog.user.vk_id}'

    api_message = api.code_confirm(code=str(code), bot_type='Telegram', bot_user_id=dialog.user.vk_id,
                                   received_from=received_from)
    await dialog.reply(api_message)

    if api_message == Messages.api_code_confirm_success or (DEBUG and code == '-1'):
        await dialog.reply(Messages.code_valid, Keyboard([[ButtonText(UserReplies.code_alice_approved)],
                                                          [ButtonText(UserReplies.code_alice_new)]]))
        dialog.user.change_page('/code-approving')
    else:
        await dialog.reply(Messages.code_invalid)


@bot.message('/code-approving')
async def code_enter(dialog: DialogData):
    if dialog.msg.text == UserReplies.code_alice_new:
        await dialog.reply(Messages.code_entry, Keyboard(empty=True))
        dialog.user.change_page('/code-enter')

    await dialog.reply(Messages.code_alice_checking)
    api_data = api.get_user_by_telegram_id(dialog.user.vk_id)

    if isinstance(api_data, dict) or (DEBUG and dialog.msg.text == 'y'):
        await dialog.reply(Messages.code_alice_ok, Keyboard([[ButtonText(x[0])] for x in UserReplies.menu_channel_keyboard]))
        await dialog.reply(Messages.help)
        dialog.user.change_page('/menu')
    elif isinstance(api_data, str) or (DEBUG and dialog.msg.text == 'n'):
        await dialog.reply(api_data)
        await dialog.reply(Messages.code_alice_error)


@bot.message('/menu')
async def menu(dialog: DialogData):
    msg = dialog.msg.text

    if msg == UserReplies.menu_channel_list:
        await dialog.reply(Messages.menu_channel_list)
        api_response = api.get_tg_feed(dialog.user.vk_id)

        if isinstance(api_response, str):
            await dialog.reply(api_response)
        else:
            feed = '\n'.join(f'{sid}. {x["source_name"]}, {x["source_url"]}' for sid, x in enumerate(api_response['feed'], start=1))

            if len(feed) != 0:
                await dialog.reply(feed)
            else:
                await dialog.reply(Messages.feed_is_empty)

    elif msg == UserReplies.menu_channel_add:
        await dialog.reply(Messages.menu_channel_add, Keyboard([[ButtonText(UserReplies.back_to_menu)]]))
        dialog.user.change_page('/feed-add')

    elif msg == UserReplies.menu_channel_delete:
        await dialog.reply(Messages.menu_channel_delete, Keyboard([[ButtonText(UserReplies.back_to_menu)]]))

        api_response = api.get_tg_feed(dialog.user.vk_id)
        if isinstance(api_response, str):
            await dialog.reply(api_response)
        else:
            feed = '\n'.join(f'{sid}. {x["source_name"]}, {x["source_url"]}' for sid, x in enumerate(api_response['feed'], start=1))

            if len(feed) != 0:
                await dialog.reply(feed, Keyboard([[ButtonText(UserReplies.back_to_menu)]]))
                dialog.user.change_page('/feed-delete')
            else:
                await dialog.reply(Messages.feed_is_empty)

    else:
        await dialog.reply(Messages.menu_use_kb, Keyboard([[ButtonText(x[0])] for x in UserReplies.menu_channel_keyboard]))


@bot.message('/feed-add')
async def feed_add(dialog: DialogData):
    text = dialog.msg.text

    if text == UserReplies.back_to_menu:
        await dialog.reply(Messages.back_to_menu, Keyboard([[ButtonText(x[0])] for x in UserReplies.menu_channel_keyboard]))
        dialog.user.change_page('/menu')
        return

    try:
        if ' ' not in text:
            raise ValueError()
        name, url = ' '.join(text.split()[:-1]), text.split()[-1]
    except Exception as e:
        await dialog.reply(Messages.feed_add_invalid)
        return

    api_response = api.add_tg_feed(dialog.user.vk_id, name, url)
    if isinstance(api_response, str):
        await dialog.reply(api_response)
    else:
        await dialog.reply(Messages.feed_add_success, Keyboard([[ButtonText(x[0])] for x in UserReplies.menu_channel_keyboard]))
        dialog.user.change_page('/menu')


@bot.message('/feed-delete')
async def feed_delete(dialog: DialogData):
    text = dialog.msg.text

    if text == UserReplies.back_to_menu:
        await dialog.reply(Messages.back_to_menu, Keyboard([[ButtonText(x[0])] for x in UserReplies.menu_channel_keyboard]))
        dialog.user.change_page('/menu')
        return

    try:
        tape_id = int(text)
    except Exception as e:
        await dialog.reply(Messages.feed_delete_invalid)
        return

    api_response = api.delete_tg_feed(dialog.user.vk_id, tape_id)
    if isinstance(api_response, str):
        await dialog.reply(api_response)
    else:
        await dialog.reply(Messages.feed_delete_success.format(api_response['deleted']['source_name']))


@bot.cmd('/stop', ADMIN_ONLY)
async def cmd_stop(dialog: DialogData, save=1):
    save = bool(save)
    if save:
        dialog.bot.save_json_db(DB_JSON)
        await dialog.reply('База данных бота успешно сохранена!')

    await dialog.reply('Инициализация выключения: бот будет остановлен через 2 секунды...')

    t = threading.Thread(target=delayed_exit, args=(2,), daemon=True)
    t.start()


@bot.cmd('/reset', ADMIN_ONLY)
async def cmd_reset(dialog: DialogData):
    dialog.bot.db_users = {}
    await dialog.reply('Database dropped')


@bot.on_forbidden()
async def forbidden(dialog: DialogData):
    await dialog.reply('Error 403: Forbidden')


@bot.on_exception()
async def exception(dialog: DialogData, exc):
    await dialog.reply(traceback.format_exc(exc))


def delayed_db_saver(bot: VkBot, delay_seconds: int = 30):
    logging.info(f'Delayed DB saver was launched. Saving DB each {delay_seconds} seconds')
    while True:
        bot.save_json_db(DB_JSON)
        time.sleep(delay_seconds)


if __name__ == '__main__':
    db_saver_thread = threading.Thread(target=delayed_db_saver, args=(bot,), daemon=True)
    db_saver_thread.start()
    bot.start(port=7778)
