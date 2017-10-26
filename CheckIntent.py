import requests
from flask import render_template


def check(route, stop, agency):
    minutes, stop_name = __get_response(route, stop, agency)

    if len(minutes) == 0:
        return render_template('no_bus_message', route=route, stop=stop, stop_name=stop_name)
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away <break time="200ms"/>' % minute)
    minute_string = ' and '.join(minute_strings)

    return render_template('bus_minutes_message', route=route, stop=stop, minutes=minute_string, stop_name=stop_name)


def __get_response(route, stop, agency):
    parameters = {
        'route': route,
        'stop': stop,
        'agency': agency
    }
    response = requests.get('https://0izohjr8ng.execute-api.us-east-2.amazonaws.com/dev/check', params=parameters)
    if response.status_code != 200:
        response.raise_for_status()

    data = response.json()
    data = data['message']
    return data['minutes'], data['stop_name']


if __name__ == '__main__':
    print check(7, 1174, 'austin-metro-bus')