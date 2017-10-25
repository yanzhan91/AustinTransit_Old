import requests
import logging as log

from requests import HTTPError


def get(user, preset, agency):
    log.info('intent_start=get')
    log.info('user=%s' % user)
    log.info('preset=%s' % preset)

    agency = agency.replace(' ', '-')

    log.info('agency=%s' % agency)

    try:
        minutes, stop_name, route, stop = __get_response(user, preset, agency)
    except HTTPError:
        raise

    log.info('api_response_start')
    log.info('minutes=%s' % minutes)
    log.info('stop_name=%s' % stop_name)
    log.info('route=%s' % route)
    log.info('stop=%s' % stop)
    log.info('api_response_end')

    if len(minutes) == 0:
        return None, stop_name, route, stop
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away <break time="200ms"/>' % minute)
    minute_string = ' and '.join(minute_strings)

    log.info('minute_string=%s' % minute_string)
    log.info('stop_name=%s' % stop_name)
    log.info('route=%s' % route)
    log.info('stop=%s' % stop)
    log.info('intent_end=get')

    return minute_string, stop_name, route, stop


def __get_response(user, preset, agency):
    parameters = {
        'user': user,
        'preset': preset,
        'agency': agency
    }
    response = requests.get('https://0izohjr8ng.execute-api.us-east-2.amazonaws.com/dev/get', params=parameters)
    if response.status_code != 200:
        log.warn('api_status_code=%s', response.status_code)
        log.warn(response.text)
        response.raise_for_status()
    data = response.json()
    data = data['message']
    return data['minutes'], data['stop_name'], data['route'], data['stop']


if __name__ == '__main__':
    print get('1234', '2', 'austin-metro-bus')
