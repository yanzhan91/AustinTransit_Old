import boto3
from boto3.dynamodb.conditions import Key


def get_bus(user_id, preset):
    user_table = boto3.resource('dynamodb').Table('AustinTransit_Users')
    response = user_table.query(
        KeyConditionExpression=Key('user_id').eq(user_id),
        Limit=1
    )

    try:
        user = response['Items'][0]
        user = user['preset ' + preset]
    except (KeyError, IndexError):
        return None, None

    return user['bus_id'], user['stop_id']

if __name__ == '__main__':
    print get_bus('123', '1')
