import requests


def get(user, preset, agency):
    minutes, stop_name, route, stop = __get_response(user, preset, agency)

    if len(minutes) == 0:
        # return render_template('no_bus_message', bus_id=route, stop_id=stop, stop_name=stop_name)
        return None, stop_name, stop_name, route, stop
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away <break time="200ms"/>' % minute)
    minute_string = ' and '.join(minute_strings)

    return minute_string, stop_name, route, stop


def __get_response(user, preset, agency):
    parameters = {
        'user': user,
        'preset': preset,
        'agency': agency
    }
    response = requests.get('https://0izohjr8ng.execute-api.us-east-2.amazonaws.com/dev/get', params=parameters)
    data = response.json()
    if data['status'] != 200 or 'message' not in data:
        # Throw error
        pass
    data = data['message']
    return data['minutes'], data['stop_name'], data['route'], data['stop']


if __name__ == '__main__':
    print get_response('123', '2', 'austin-metro-bus')
