import boto3
import os

dynamodb = boto3.resource('dynamodb')

def get_table(table_env="PETS_TABLE"):
    """
    Retorna a tabela DynamoDB baseada na variável de ambiente.

    Uso:
        get_table()              → usa PETS_TABLE (padrão - pets)
        get_table("TABLE_NAME")  → usa TABLE_NAME (inventory)
    """
    table_name = os.environ[table_env]
    return dynamodb.Table(table_name)