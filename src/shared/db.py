import boto3
import os
 
dynamodb = boto3.resource('dynamodb')
 
def get_table():
    return dynamodb.Table(os.environ["PETS_TABLE"])
