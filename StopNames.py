import logging
import boto3
from boto3.dynamodb.conditions import Key


def get_stop_name(stop_id):
    logging.info('Geting stop name for %s' % stop_id)
    try:
        user_table = boto3.resource('dynamodb').Table('TransitBuddy_Stops')
        response = user_table.query(
            KeyConditionExpression=Key('stop_id').eq(int(stop_id)),
            Limit=1
        )
        return response['Items'][0]['stop_name']
    except Exception as e:
        logging.info(e)
        return ''


if __name__ == "__main__":
    print(get_stop_name('1176'))
