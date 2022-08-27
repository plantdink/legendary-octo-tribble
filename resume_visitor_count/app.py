import json
import logging
import boto3
from botocore.exceptions import ClientError


# Initialize dynamodb boto3 object
dynamodb = boto3.resource('dynamodb')

# Set dynamodb table name variable from env
ddb_table_name = 'visitors_cloud'
key_name = 'ID'

table = dynamodb.Table(ddb_table_name)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    # Update item in table or add if doesn't exist
    try:
        response = table.update_item(
            TableName=ddb_table_name,
            Key={
                key_name: 'visitor_count'
            },
            ExpressionAttributeValues={
                ':inc': 1,
                ':zero': 0
            },
            # Expression for DynamoDB to create the visitor_count attribute if it doesn't exist, or increment it by 1 if it does exist
            UpdateExpression="SET visitor_count = if_not_exists(visitor_count, :zero) + :inc",
            ReturnValues="UPDATED_NEW"
        )
        
        # Format dynamodb response into variable, change number to int
        responseBody = json.dumps(
            {
                "visitor_count": int(response["Attributes"]["visitor_count"])
            }
        )
        
        # Create api response object
        apiResponse = {
            "isBase64Encoded": False,
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET',
                'Content-Type': 'application/json'
            },
            "body": responseBody
        }

    # error handler
    except ClientError as err:
        logger.error(
            f"Couldn't update Visitor Count in {table}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}" 
        )
        raise
    else:
    # Return api response object
        return apiResponse