import requests


def add(user, route, stop, preset, agency):
    agency = agency.replace(' ', '-')

    response = __get_response(user, route, stop, preset, agency)
    if response.status_code != 200:
        response.raise_for_status()


def __get_response(user, route, stop, preset, agency):
    parameters = {
        'user': user,
        'route': route,
        'stop': stop,
        'preset': preset,
        'agency': agency
    }
    response = requests.post('https://0izohjr8ng.execute-api.us-east-2.amazonaws.com/dev/add', data=parameters)
    return response


if __name__ == '__main__':
    print add('123', 7, 1174, '1', 'austin-metro-bus')
