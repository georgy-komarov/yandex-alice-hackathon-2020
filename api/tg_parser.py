import configparser
import json
from sys import argv

from telethon.sync import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

# Присваиваем значения внутренним переменным
api_id = 1642232
api_hash = '900fd3642351f310a20626064874aff6'
username = 'prokhn'

client = TelegramClient(username, api_id, api_hash)

client.start()


def dump_all_messages(channel, count=50):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0  # номер записи, с которой начинается считывание
    limit_msg = count  # максимальное число записей, передаваемых за один раз

    all_messages = []  # список всех сообщений
    total_messages = 0
    total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

    class DateTimeEncoder(json.JSONEncoder):
        '''Класс для сериализации записи дат в JSON'''

        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    history = client(GetHistoryRequest(
        peer=channel,
        offset_id=offset_msg,
        offset_date=None, add_offset=0,
        limit=limit_msg, max_id=0, min_id=0,
        hash=0))

    messages = history.messages
    for message in messages:
        all_messages.append(message.to_dict())

    return json.dumps(all_messages, ensure_ascii=False, cls=DateTimeEncoder)


if __name__ == '__main__':
    print(dump_all_messages(client.get_entity(argv[1])))
