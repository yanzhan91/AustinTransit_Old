import boto3
from boto3.dynamodb.conditions import Key


def get_bus(user_id, preset):
    user_table = boto3.resource('dynamodb').Table('AustinTransit_Users')
    response = user_table.query(
        KeyConditionExpression=Key('user_id').eq(user_id),
        Limit=1
    )

    user = response['Items'][0][preset]

    return int(user['bus_id']), int(user['stop_id'])


if __name__ == '__main__':
    print get_bus('123', 'Preset One')
