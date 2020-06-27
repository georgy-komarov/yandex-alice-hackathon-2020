from base_skill.skill import *
from .state import State
from .strings import *
from .api import API
import logging

# logger = logging.getLogger(__name__)

handler = CommandHandler()
api = API('https://alice-hackathon.komarov.ml/api/')


@handler.hello_command
def hello(req, res, session):
    uid = req.user_id
    user_exists, tg_id, vk_id = api.get_user(uid)

    if not (tg_id or vk_id):
        res.text = f'Привет! Я помогу следить за последними публикациями в Ваших любимых ' \
            f'Телеграм-каналах или пабликах Вконтакте. Для начала нужно связать ваш аккаунт с Телеграм-ботом или ботом Вконтакте. Вы готовы?'
        session['state'] = State.SEND_CODE
    else:
        res.text = TEXT_MENU
        session['state'] = State.START


@handler.command(words=tkn(WORDS_NO), states=State.SEND_CODE)
def finish(req, res, session):
    res.text = 'Очень жаль! Когда будете готовы - сообщите мне об этом.'


@handler.undefined_command(states=State.SEND_CODE)
def send_code(req, res, session):
    uid = req.user_id
    code = ' '.join(list(api.generate_code(uid)))
    res.text = f'Найдите в Телеграме или во Вконтакте бота, который называется "Моя лента Алиса" и отправьте ему следующий код: {code}.'
    res.text += ' Затем скажите фразу: готово или повтори код, если вы его не расслышали.'
    session['state'] = State.WAIT_FOR_CODE
    session['code'] = code


@handler.command(words=tkn(WORDS_REPEAT), states=State.WAIT_FOR_CODE)
def ready(req, res, session):
    res.text = f'Повторяю, ваш код: {session["code"]}. '
    res.text += f'После ввода, скажите мне, что вы готовы.'


@handler.command(words=tkn(WORDS_READY), states=State.WAIT_FOR_CODE)
def ready(req, res, session):
    # спрашиваем про то кто ввел код
    uid = req.user_id
    success, msg = api.check_message(uid)
    if success:
        res.text = f'{msg} - это ваш аккаунт?'
        session['state'] = State.READY
    else:
        res.text = 'Никто пока не подтверждал Ваш код.'
        session['state'] = State.WAIT_FOR_CODE


@handler.command(words=tkn(WORDS_YES), states=State.READY)
def yes(req, res, session):
    # Успешно подключен аккаунт - переход в меню
    uid = req.user_id
    success = api.complete(uid)
    res.text = TEXT_CONNECT + ' ' + TEXT_MENU
    session['state'] = State.START


@handler.command(words=tkn(WORDS_NO), states=State.READY)
def no(req, res, session):
    uid = req.user_id
    # Все плохо, перегенерация кода
    code = ' '.join(list(api.generate_code(uid)))
    session['code'] = code
    res.text = f'Ваш новый код: {code}. Сообщите его боту.'
    session['state'] = State.WAIT_FOR_CODE


@handler.command(words=tkn(WORDS_START), states=State.START)
def start_listening(req, res, session):
    uid = req.user_id
    channel, msg = api.get_msg(uid)
    res.text = f'Канал {channel}. {msg}'
    session['state'] = State.ACTION


@handler.command(words=tkn(WORDS_NEXT), states=State.ACTION)
def next(req, res, session):
    uid = req.user_id
    channel, msg = api.get_msg(uid)
    res.text = f'Канал {channel}. {msg}'


@handler.command(words=tkn(WORDS_LIKE), states=State.ACTION)
def like(req, res, session):
    uid = req.user_id
    channel, msg = api.get_msg(uid)
    res.text = f'Вам понравился предыдущий пост. Присылаю следующий. Канал {channel}. {msg}'


@handler.command(words=tkn(WORDS_DISLIKE), states=State.ACTION)
def dislike(req, res, session):
    uid = req.user_id
    channel, msg = api.get_msg(uid)
    res.text = f'Вам не понравился предыдущий пост. Присылаю следующий. Канал {channel}. {msg}'


@handler.command(words=tkn(WORDS_STOP), states=State.ACTION)
def like(req, res, session):
    res.text = 'Прослушивание постов завершено. Приходите еще! ' + TEXT_MENU
    session['state'] = State.START


@handler.undefined_command(states=State.ALL)
def wtf(res, req, session):
    res.text = txt(TEXT_WTF.get(session['state'], 'Извините, я вас не поняла'))


class MyFeed(BaseSkill):
    name = 'alice'
    command_handler = handler
