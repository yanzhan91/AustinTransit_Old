import requests
import logging as log
from flask import render_template

from requests import HTTPError


def get(user, preset, agency):
    try:
        minutes, stop_name, route, stop = __get_response(user, preset, agency)
    except HTTPError as e:
        if e.response.json()['error_code'] == 10302:
            return render_template('preset_not_found_message', preset=preset, agency=agency)
        else:
            return render_template('internal_error_message')

    if len(minutes) == 0:
        return render_template('no_route_message', bus_id=route, stop_id=stop, stop_name=stop_name)

    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away <break time="200ms"/>' % minute)
    minute_string = ' and '.join(minute_strings)

    return render_template('check_success_message', route=route, stop=stop, minutes=minute_string,
                           stop_name=stop_name)


def __get_response(user, preset, agency):
    parameters = {
        'user': user,
        'preset': preset,
        'agency': agency
    }
    response = requests.get('https://0izohjr8ng.execute-api.us-east-2.amazonaws.com/dev/get', params=parameters)
    if response.status_code != 200:
        response.raise_for_status()
    data = response.json()
    data = data['message']
    return data['minutes'], data['stop_name'], data['route'], data['stop']


if __name__ == '__main__':
    print get('1234', '2', 'austin-metro-bus')
