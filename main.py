from flask import Flask, render_template
from flask_ask import Ask, statement, question, context, session
import re

from requests import HTTPError

import CheckIntent
import SetIntent
import GetIntent


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
    session.attributes['request'] = 'check'
    session.attributes['agency'] = agency

    result = analyze_id(route, 'route')
    if result:
        session.attributes['current_param'] = 0
        return result
    result = analyze_id(stop, 'stop')
    if result:
        session.attributes['current_param'] = 1
        return result

    minute_string, stop_name = CheckIntent.check(session.attributes['route'], session.attributes['stop'],
                                                 'austin-%s' % agency)

    minutes_message = render_template('bus_minutes_message', route=route, stop=stop, minutes=minute_string,
                                      stop_name=stop_name)

    return generate_statement_card(minutes_message, 'Check Status')


@ask.intent('SetIntent')
def set_intent(route, stop, preset, agency):
    session.attributes['request'] = 'set'
    session.attributes['agency'] = agency

    result = analyze_id(route, 'route')
    if result:
        session.attributes['current_param'] = 1
        return result
    result = analyze_id(stop, 'stop')
    if result:
        session.attributes['current_param'] = 2
        return result
    result = analyze_id(preset, 'preset')
    if result:
        session.attributes['current_param'] = 3
        return result

    try:
        SetIntent.add(context.System.user.userId, session.attributes['route'], session.attributes['stop'],
                      session.attributes['preset'], 'austin-%s' % agency)
    except HTTPError:
        return statement(render_template('internal_error_message'))

    set_bus_success_message = render_template('set_bus_success_message',
                                              route=route, stop=stop, preset=preset, agency=agency)

    return generate_statement_card(set_bus_success_message, 'Set Bus Status')


@ask.intent('GetIntent')
def get_intent(preset, agency):
    session.attributes['request'] = 'get'
    session.attributes['agency'] = agency

    if not preset:
        preset = '1'

    param_check_fail = analyze_id(preset, 'preset')
    if param_check_fail:
        session.attributes['current_param'] = 1
        return param_check_fail

    try:
        minute_string, stop_name, route, stop = GetIntent.get(context.System.user.userId, session.attributes['preset'],
                                                              'austin-%s' % agency)
    except HTTPError as e:
        if e.response.json()['error_code'] == 10302:
            return statement(render_template('preset_not_found_message', preset=preset, agency=agency))
        else:
            return statement(render_template('internal_error_message'))

    if not minute_string:
        return generate_statement_card(
            render_template('no_bus_message', bus_id=route, stop_id=stop, stop_name=stop_name), 'Get Intent')

    minutes_message = render_template('bus_minutes_message', claire='', route=route, stop=stop, minutes=minute_string,
                                      stop_name=stop_name)

    return generate_statement_card(minutes_message, 'Get Bus Status')


@ask.intent('AnswerIntent')
def answer_intent(num):
    if check_iteration():
        return statement(render_template('try_again_message'))

    agency = session.attributes['agency']

    current_param = session.attributes['current_param']
    if session.attributes['request'] == 'check':
        return CheckIntent.check(
            assign_params(current_param, 0, num),
            assign_params(current_param, 1, num),
            agency)
    elif session.attributes['request'] == 'set':
        return SetIntent.add(
            context.System.user.userId,
            assign_params(current_param, 1, num),
            assign_params(current_param, 2, num),
            assign_params(current_param, 3, num),
            agency)
    elif session.attributes['request'] == 'get':
        return GetIntent.get(
            context.System.user.userId,
            assign_params(current_param, 1, num),
            agency)
    else:
        return question(render_template('try_again_message'))


def assign_params(current_param, param_num, value):
    return value if current_param == param_num else None


def analyze_id(value, param):
    if param in session.attributes:  # check if param already in session
        return None
    if not value:
        return question(render_template('%s-question' % param))\
            .reprompt(render_template('%s-question-reprompt' % param))

    if not re.compile('\\d+').match(str(value)):
        return question(render_template('%s-question' % param)) \
            .reprompt(render_template('%s-question-reprompt' % param))

    session.attributes[param] = value
    return None


def generate_statement_card(speech, title):
    return statement(speech).simple_card(title, remove_html(speech))


def remove_html(text):
    return re.sub('<[^<]*?>|\\n', '', text)


def check_iteration():
    if 'iter' not in session.attributes:
        session.attributes['iter'] = 1
        return False
    if session.attributes['iter'] > 2:
        return True
    session.attributes['iter'] += 1


if __name__ == '__main__':
    app.config['ASK_VERIFY_REQUESTS'] = False
    app.run()
