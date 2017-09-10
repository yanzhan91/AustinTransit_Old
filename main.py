import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question, context
import uuid
import re
import CheckBusIntent
import SetBusIntent
import GetBusIntent


app = Flask(__name__)
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
def check_bus(bus_id, stop_id):
    logger.info('session = %s' % session_id)
    logger.info('%s: Checking Bus %s at %s...' % (session_id, bus_id, stop_id))
    minutes = CheckBusIntent.check_bus(bus_id, stop_id)
    logging.info('%s: Minutes received: %s' % (session_id, minutes))
    if len(minutes) == 0:
        no_bus_message = render_template('no_bus_message', bus_id=bus_id, stop_id=stop_id)
        return statement(no_bus_message).simple_card('Check Bus Status', remove_html(no_bus_message))
    minutes_string = ' and '.join(str(x) for x in minutes)
    bus_minutes_message = render_template('bus_minutes_message', bus_id=bus_id, stop_id=stop_id, minutes=minutes_string)
    return statement(bus_minutes_message).simple_card('Check Bus Status', remove_html(bus_minutes_message))


@ask.intent('SetBusIntent')
def set_bus(bus_id, stop_id, preset):
    preset = check_preset_syntax(preset)
    logger.info('session = %s' % session_id)
    logger.info('%s: Setting Bus %s at %s for %s...' % (session_id, bus_id, stop_id, preset))
    try:
        SetBusIntent.set_bus(context.System.user.userId, bus_id, stop_id, preset)
    except Exception as e:
        logger.error(e)
        internal_error_message = render_template('internal_error_message')
        return statement(internal_error_message).simple_card('Set Bus Status', internal_error_message)
    logger.info('%s: Set bus %s at %s was successful' % (session_id, bus_id, stop_id))
    set_bus_success_message = render_template('set_bus_success_message', bus_id=bus_id, stop_id=stop_id, preset=preset)
    return statement(set_bus_success_message).simple_card('Set Bus Status', remove_html(set_bus_success_message))


@ask.intent('GetBusIntent')
def get_bus(preset):
    preset = check_preset_syntax(preset)
    logger.info('session = %s' % session_id)
    logger.info('%s: Getting Bus at %s...' % (session_id, preset))
    try:
        bus_id, stop_id = GetBusIntent.get_bus(context.System.user.userId, preset)
        logger.info('%s: Bus retrieved was %s at %s' % (session_id, bus_id, stop_id))
        return check_bus(bus_id, stop_id)
    except Exception as e:
        logger.error(e)
        internal_error_message = render_template('internal_error_message')
        return statement(internal_error_message).simple_card('Get Bus Status', internal_error_message)


@ask.intent('GetPresetIntent')
def get_preset(preset):
    preset = check_preset_syntax(preset)
    bus_id, stop_id = GetBusIntent.get_bus(context.System.user.userId, preset)
    get_preset_message = render_template('get_preset_message', preset=preset, bus_id=bus_id, stop_id=stop_id)
    return statement(get_preset_message).simple_card(preset.title(), remove_html(get_preset_message))


def check_preset_syntax(preset):
    if not preset and not re.compile('preset\\s[0-9]+').match(preset):
        return 'preset 1'
    elif preset == 'preset to':
        return 'preset 2'
    elif preset == 'preset too':
        return 'preset 2'
    else:
        return preset


def remove_html(text, return_char=True):
    if return_char:
        regex = '<[^<]*?>|\\n'
    else:
        regex = '<[^<]*?>'
    return re.sub(regex, '', text)
