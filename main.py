from flask import Flask, render_template
from flask_ask import Ask, statement, question, context, request

import re
import json
import os

import CheckIntent
import SetIntent
import GetIntent

import logging as log

app = Flask(__name__)
ask = Ask(app, '/')


@ask.launch
def launch():
    welcome_text = render_template('welcome')
    return question(welcome_text)\
        .simple_card('Welcome to AustinTransit', remove_html(welcome_text))\
        .reprompt(render_template('help'))


@ask.intent('AMAZON.HelpIntent')
def help_intent():
    return question(render_template('help')).simple_card('AustinTransit Help', render_template('help_card'))


@ask.intent('AMAZON.StopIntent')
def stop_intent():
    return statement('ok')


@ask.intent('CheckIntent')
def check_intent(route, stop, agency):
    log.info('Request object = %s' % request)
    if request['dialogState'] != 'COMPLETED':
        return delegate_dialog()
    message = CheckIntent.check(route, stop, '%s-%s' % (os.environ['city'], agency.replace(' ', '-')))
    log.info('Response message = %s', message)
    return generate_statement_card(message, 'Check Status')


@ask.intent('SetIntent')
def set_intent(route, stop, preset, agency):
    log.info('Request object = %s' % request)
    if request['dialogState'] != 'COMPLETED':
        return delegate_dialog()
    message = SetIntent.add(context.System.user.userId, route, stop, preset,
                            '%s-%s' % (os.environ['city'], agency.replace(' ', '-')))
    log.info('Response message = %s', message)
    return generate_statement_card(message, 'Set Status')


@ask.intent('GetIntent')
def get_intent(preset, agency):
    log.info('Request object = %s' % request)
    if request['dialogState'] != 'COMPLETED':
        return delegate_dialog()

    message = GetIntent.get(context.System.user.userId, preset,
                            '%s-%s' % (os.environ['city'], agency.replace(' ', '-')))
    log.info('Response message = %s', message)
    return generate_statement_card(message, 'Get Status')


def generate_statement_card(speech, title):
    return statement(speech).simple_card(title, remove_html(speech))


def remove_html(text):
    return re.sub('<[^<]*?>|\\n', '', text)


def delegate_dialog():
    return json.dumps({'response': {'directives': [{'type': 'Dialog.Delegate'}],
                                    'shouldEndSession': False}, 'sessionAttributes': {}})

if __name__ == '__main__':
    app.config['ASK_VERIFY_REQUESTS'] = False

    json_data = open('zappa_settings.json')
    env_vars = json.load(json_data)['test']['environment_variables']
    for key, val in env_vars.items():
        os.environ[key] = val

    app.run()
