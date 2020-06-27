from flask import Flask, redirect, request
from base_skill.skill import Response, Request
from myfeed.main import MyFeed
import logging
import json
logging.basicConfig(filename='error.log',level=logging.DEBUG)

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>Bruh!!!!</h1>"

SKILLS = [MyFeed()]
skill_dict = {skill.name: skill for skill in SKILLS}
sessionStorage = {
    skill.name: {} for skill in SKILLS
}


@app.route('/<skill>', methods=['POST'])
def main(skill):
    if skill in skill_dict:
        req = request.json
        return handle_dialog(req, skill_dict[skill])
    return '404'


def prepare_res(req):
    return {
        'session': req['session'],
        'version': req['version'],
        'response': {
            'end_session': False
        }
    }


def ping(req, res):
    return req.text == 'ping'


def handle_dialog(req, skill):
    res = Response(prepare_res(req))
    req = Request(req)
    session = sessionStorage[skill.name]
    user_id = req.user_id

    if not ping(req, res):
        if req.new_session:
            session[user_id] = {}
            skill.command_handler.hello.execute(req=req, res=res, session=session[user_id])
        else:
            if user_id not in session:
                session[user_id] = {}

            skill.command_handler.execute(req=req, res=res, session=session[user_id])

        skill.log(req=req, res=res, session=session[user_id])
    else:
        res.text = 'pong'

    return json.dumps(res.res)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
