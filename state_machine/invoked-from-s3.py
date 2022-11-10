import json
import urllib

def lambda_handler(event, context):
    # TODO implement
    print("Event = ", event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(key)
    print(bucket)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
