import requests
from requests.models import Response
from message_strings import Messages
from typing import Union, Dict, Any


class API:
    def __init__(self, host: str):
        self.host = host

    def get_user_by_telegram_id(self, tg_id: int) -> Union[str, Dict[str, str]]:
        resp = self.get(f'/user/telegram/{tg_id}')
        return self._get_user('tg_id', tg_id, resp)

    def get_user_by_vk_id(self, vk_id: int) -> Union[str, Dict[str, str]]:
        resp = self.post(f'/user/vk/{vk_id}')
        return self._get_user('vk_id', vk_id, resp)

    def _get_user(self, account_type: str, user_id: int, resp: Response):
        if resp.status_code != 200:
            return Messages.api_bad_status_code.format(resp.status_code)

        data = resp.json()
        if not data['exists']:
            return Messages.api_user_not_exists

        return data

    def code_confirm(self, code: str, bot_type: str, received_from: str, bot_user_id: int) -> str:
        resp = self.post(f'/code/confirm', code=code, bot_type=bot_type, received_from=received_from, bot_user_id=bot_user_id)

        if resp.status_code != 200:
            return Messages.api_bad_status_code.format(resp.status_code)

        data = resp.json()
        if data['success']:
            return Messages.api_code_confirm_success
        else:
            return Messages.api_code_confirm_fail

    def get_tg_feed(self, tg_id: int) ->:
        resp = self.get(f'/user/telegram/{tg_id}/feed')
        if resp.status_code != 200:
            return Messages.api_bad_status_code

        data = resp.json()
        if data['success']:
            return data
        else:
            return Messages.api_feed_get_fail

    def get_vk_feed(self, vk_id: int):
        resp = self.get(f'/user/vk/{vk_id}/feed')
        if resp.status_code != 200:
            return Messages.api_bad_status_code

        data = resp.json()
        if data['success']:
            return data
        else:
            return Messages.api_feed_get_fail

    def add_tg_feed(self, tg_id: int, tape_name: str, tape_url: str):
        resp = self.post(f'/user/telegram/{tg_id}/feed/add', tape_name=tape_name, tape_url=tape_url)
        if resp.status_code != 200:
            return Messages.api_bad_status_code

        data = resp.json()
        if data['success']:
            return data
        else:
            return Messages.api_feed_add_fail

    def add_vk_feed(self, vk_id: int, group_name: str, group_id: int):
        resp = self.post(f'/user/vk/{vk_id}/feed/add', group_name=group_name, group_id=group_id)
        if resp.status_code != 200:
            return Messages.api_bad_status_code

        data = resp.json()
        if data['success']:
            return data
        else:
            return Messages.api_feed_add_fail

    def delete_tg_feed(self, tg_id: int, tape_id: int):
        resp = self.post(f'/user/telegram/{tg_id}/feed/delete', tape_id=tape_id)
        if resp.status_code != 200:
            return Messages.api_bad_status_code

        data = resp.json()
        if data['success']:
            return data
        else:
            return Messages.api_feed_delete_fail

    def delete_vk_feed(self, vk_id: int, group_id: int):
        resp = self.post(f'/user/мл/{vk_id}/feed/delete', group_id=group_id)
        if resp.status_code != 200:
            return Messages.api_bad_status_code

        data = resp.json()
        if data['success']:
            return data
        else:
            return Messages.api_feed_delete_fail

    def get(self, method: str, **kwargs) -> Response:
        return self._method('get', method, **kwargs)

    def post(self, method: str, **kwargs) -> Response:
        return self._method('post', method, **kwargs)

    def _method(self, http: str, method: str, **kwargs) -> Response:
        if http == 'get':
            resp = requests.get(self.host + method, params=kwargs)
        elif http == 'post':
            resp = requests.post(self.host + method, data=kwargs)
        else:
            raise ValueError()

        return resp


if __name__ == '__main__':
    api = API('https://alice-hackathon.komarov.ml/api')

    # print(api.get_user_by_telegram_id(1))
    # print(api.get_user_by_vk_id(1))
    print(api.code_confirm(received_from='Fname last name', code='700342', bot_type='Telegram', bot_user_id=5))
