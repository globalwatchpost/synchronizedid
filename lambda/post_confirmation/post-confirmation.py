import json
import boto3
import logging

logger = logging.getLogger()

def post_confirmation_trigger(event, context):
    
    logger.info( "Fired with post confirmation trigger" )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
