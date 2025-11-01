import boto3
import os
from dotenv import load_dotenv

# Load AWS credentials
load_dotenv()

dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1')

def create_table():
    try:
        response = dynamodb.create_table(
            TableName="Payments",
            KeySchema=[
                {"AttributeName": "transaction_id", "KeyType": "HASH"}  # Partition key
            ],
            AttributeDefinitions=[
                {"AttributeName": "transaction_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        print("✅ Table creation started:", response['TableDescription']['TableName'])
    except dynamodb.exceptions.ResourceInUseException:
        print("⚠️ Table already exists.")

if __name__ == "__main__":
    create_table()
