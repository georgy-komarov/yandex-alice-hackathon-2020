from requests import get
import re


class API:
    def __init__(self, host):
        self.host = host
        pass

    def get_user(self, yid):
        response = get(self.host + f'user/{yid}/').json()
        return response['exists'], response['tg_id'], response['vk_id']

    def generate_code(self, yid):
        return get(self.host + f'user/{yid}/code/generate/').json()['code']

    def check_message(self, yid):
        response = get(self.host + f'user/{yid}/code/check/').json()
        return response['success'], response['message']

    def complete(self, yid):
        response = get(self.host + f'user/{yid}/code/complete/').json()
        return response['success']

    def get_msg(self, yid):
        response = get(self.host + f'user/{yid}/message/').json()
        msg = response['message']
        text = re.sub(r'^https?:\/\/.*[\r\n]*', '', msg, flags=re.MULTILINE)
        return response['channel_name'], text
