import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, context
import uuid
import CheckBusIntent
import SetBusIntent
import GetBusIntent


app = Flask(__name__)
ask = Ask(app, '/')
logger = logging.getLogger()
session_id = uuid.uuid4()


@ask.launch
def launch():
    print('Hello')


@ask.intent('CheckBusIntent', convert={'bus_id': int, 'stop_id': int})
def check_bus(bus_id, stop_id):
    logger.info('session = %s' % session_id)
    logger.info('%s: Checking Bus %s at %s...' % (session_id, bus_id, stop_id))
    minutes = CheckBusIntent.check_bus(bus_id, stop_id)
    logging.info('%s: Minutes received: %s' % (session_id, minutes))
    if len(minutes) == 0:
        return statement(render_template('no_bus_message', bus_id=bus_id, stop_id=stop_id))
    minutes_string = ' and '.join(str(x) for x in minutes)
    return statement(render_template('bus_minutes_message', bus_id=bus_id, stop_id=stop_id, minutes=minutes_string))


@ask.intent('SetBusIntent')
def set_bus(bus_id, stop_id, preset):
    logger.info('session = %s' % session_id)
    logger.info('%s: Setting Bus %s at %s...' % (session_id, bus_id, stop_id))
    try:
        SetBusIntent.set_bus(context.System.user.userId, bus_id, stop_id, preset)
    except Exception as e:
        logger.error(e)
        return statement(render_template('internal_error_message'))
    logger.info('%s: Set bus %s at %s was successful' % (session_id, bus_id, stop_id))
    return statement(render_template('set_bus_success_message', bus_id=bus_id, stop_id=stop_id))


@ask.intent('GetBusIntent')
def get_bus(preset):
    logger.info('session = %s' % session_id)
    logger.info('%s: Getting Bus...')
    try:
        bus_id, stop_id = GetBusIntent.get_bus(context.System.user.userId, preset)
        logger.info('%s: Bus retrieved was %s at %s' % (session_id, bus_id, stop_id))
        return check_bus(bus_id, stop_id)
    except Exception as e:
        logger.error(e)
        return statement(render_template('internal_error_message'))
