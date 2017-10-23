import requests


def add(user, route, stop, preset, agency):
    response = __get_response(user, route, stop, preset, agency)
    if response['status'] != 200:
        raise Exception
        # return render_template('internal_error_message')
    # return render_template('set_bus_success_message', route=route, stop=stop, preset=preset)


def __get_response(user, route, stop, preset, agency):
    parameters = {
        'user': user,
        'route': route,
        'stop': stop,
        'preset': preset,
        'agency': agency
    }
    response = requests.post('https://0izohjr8ng.execute-api.us-east-2.amazonaws.com/dev/add', data=parameters)
    return response.json()


if __name__ == '__main__':
    print add('123', 7, 1174, '1', 'austin-metro-bus')
