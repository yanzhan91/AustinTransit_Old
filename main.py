import logging
from flask import Flask, render_template, request
from flask_ask import Ask, statement, question, context, session
import uuid
import re
import json
import CheckBusIntent
import SetBusIntent
import GetBusIntent
import StopNames


app = Flask(__name__)
app.config['ASK_VERIFY_REQUESTS'] = False
ask = Ask(app, '/')
logger = logging.getLogger()
session_id = uuid.uuid4()


@ask.launch
def launch():
    welcome_text = render_template('welcome')
    return question(welcome_text)\
        .simple_card('Welcome to AustinTransit', remove_html(welcome_text))\
        .reprompt(render_template('help'))


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    return question(help_text).simple_card('AustinTransit Help', remove_html(help_text, False))


@ask.intent('CheckBusIntent', convert={'bus_id': int, 'stop_id': int})
def check_bus_intent(bus_id, stop_id):
    bus_minutes_message = check_bus(bus_id, stop_id)
    return generate_statement_card(bus_minutes_message, 'Check Bus Status', remove_html(bus_minutes_message))


@ask.intent('SetBusIntent')
def set_bus_intent(num):
    if 'question' not in session.attributes:
        session.attributes['question'] = 'bus'
        return question('For which bus id?').reprompt('For a list of bus IDs, say help.')
    elif session.attributes['question'] == 'bus':
        session.attributes['question'] = 'stop'
        session.attributes['bus'] = num
        return question('And which stop id?').reprompt('For a list of stop IDs, say help.')
    elif session.attributes['question'] == 'stop':
        session.attributes['question'] = 'preset'
        session.attributes['stop'] = num
        return question('Which preset').reprompt('Which preset would you like to save this in?')
    elif session.attributes['question'] == 'preset':
        session.attributes['preset'] = num

    set_bus_success_message = \
        set_bus(session.attributes['bus'], session.attributes['stop'], 'preset %s' % session.attributes['preset'])
    return generate_statement_card(set_bus_success_message, 'Set Bus Status', remove_html(set_bus_success_message))


@ask.intent('GetBusIntent')
def get_bus_intent(preset):
    get_bus_message = get_bus(preset)
    return generate_statement_card(get_bus_message, 'Get Bus Status', get_bus_message)


@ask.intent('GetPresetIntent')
def get_preset_intent(preset):
    get_preset_message = get_bus(preset)
    return generate_statement_card(get_preset_message, preset.title(), remove_html(get_preset_message))


def check_bus(bus_id, stop_id):
    logger.info('session = %s' % session_id)
    logger.info('%s: Checking Bus %s at %s...' % (session_id, bus_id, stop_id))
    minutes = CheckBusIntent.check_bus(bus_id, stop_id)
    logging.info('%s: Minutes received: %s' % (session_id, minutes))
    if len(minutes) == 0:
        return render_template('no_bus_message', bus_id=bus_id, stop_id=stop_id,
                               stop_name=StopNames.get_stop_name(stop_id))
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away <break time="200ms"/>' % minute)
    minute_string = ' and '.join(minute_strings)
    return render_template('bus_minutes_message', bus_id=bus_id, stop_id=stop_id, minutes=minute_string,
                           stop_name=StopNames.get_stop_name(stop_id))


def set_bus(bus_id, stop_id, preset):
    preset = check_preset_syntax(preset)
    logger.info('session = %s' % session_id)
    logger.info('%s: Setting Bus %s at %s for %s...' % (session_id, bus_id, stop_id, preset))
    try:
        SetBusIntent.set_bus(context.System.user.userId, bus_id, stop_id, preset)
    except Exception as e:
        logger.error(e)
        return render_template('internal_error_message')
    logger.info('%s: Set bus %s at %s was successful' % (session_id, bus_id, stop_id))
    set_bus_success_message = render_template('set_bus_success_message', bus_id=bus_id, stop_id=stop_id, preset=preset,
                                              stop_name=StopNames.get_stop_name(stop_id))
    return set_bus_success_message


def get_bus(preset):
    # preset = check_preset_syntax(preset)
    logger.info('session = %s' % session_id)
    logger.info('%s: Getting Bus at preset %s...' % (session_id, preset))
    try:
        bus_id, stop_id = GetBusIntent.get_bus(context.System.user.userId, preset)
        logger.info('%s: Bus retrieved was %s at %s' % (session_id, bus_id, stop_id))
        if not bus_id or not stop_id:
            return render_template('preset_not_found_message', preset=preset)
        return check_bus(bus_id, stop_id)
    except Exception as e:
        logger.error(e)
        return render_template('internal_error_message')


def get_preset(preset):
    # preset = check_preset_syntax(preset)
    bus_id, stop_id = GetBusIntent.get_bus(context.System.user.userId, preset)
    return render_template('get_preset_message', preset=preset, bus_id=bus_id, stop_id=stop_id,
                           stop_name=StopNames.get_stop_name(stop_id))


def generate_statement_card(speech, title, card):
    return statement(speech).simple_card(title, remove_html(card))


# def check_preset_syntax(preset):
#     if preset == 'preset to':
#         return 'preset 2'
#     elif preset == 'preset too':
#         return 'preset 2'
#     elif not preset or not re.compile('preset\\s[0-9]+').match(preset):
#         return 'preset 1'
#     else:
#         return preset


def remove_html(text, return_char=True):
    if return_char:
        regex = '<[^<]*?>|\\n'
    else:
        regex = '<[^<]*?>'
    return re.sub(regex, '', text)

# WebHook


@app.route('/webhook', methods=['POST'])
def webhook():
    print(json.dumps(request.json))

    try:
        request_json = request.json
        parameters = request_json['result']['parameters']
        intent_name = request_json['result']['metadata']['intentName']
    except Exception as e:
        logger.error(e)
        return webhook_error_response()

    if intent_name == 'CheckBusIntent':
        return webhook_check(parameters)
    elif intent_name == 'SetBusIntent':
        return webhook_set(parameters)
    elif intent_name == 'GetBusIntent':
        return webhook_get(parameters)
    else:
        return webhook_error_response()


def webhook_check(parameters):
    try:
        bus_id = parameters['bus_id']
        stop_id = parameters['stop_id']
    except Exception as e:
        logger.error(e)
        return webhook_missing_key_response()
    return webhook_get_response(check_bus(bus_id, stop_id))


def webhook_set(parameters):
    try:
        bus_id = parameters['bus_id']
        stop_id = parameters['stop_id']
    except Exception as e:
        logger.error(e)
        return webhook_missing_key_response
    preset = parameters['preset']
    return webhook_get_response(set_bus(bus_id, stop_id, preset))


def webhook_get(parameters):
    preset = parameters['preset']
    return webhook_get_response(get_bus(preset))


def webhook_get_response(response):
    response_text = remove_html(response, True)
    return webhook_format_response(response_text)


def webhook_format_response(text):
    return json.dumps({
        'speech': text,
        'displayText': text
    })


def webhook_error_response():
    return webhook_format_response(render_template('internal_error_message'))


def webhook_missing_key_response():
    return webhook_format_response(render_template('missing_required_values'))


if __name__ == '__main__':
    app.run()
