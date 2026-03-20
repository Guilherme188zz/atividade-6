from boto3.dynamodb.conditions import Attr
from src.shared.response import success, error
import boto3
import os


def get_history_table():
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ["HISTORY_TABLE_NAME"]
    return dynamodb.Table(table_name)


def handler(event, context):
    """
    GET /inventory/{id}/history
    Retorna o histórico de movimentações de um item.
    """
    try:
        item_id = event["pathParameters"]["id"]
        table = get_history_table()

        response = table.scan(
            FilterExpression=Attr("itemId").eq(item_id)
        )

        # Ordena por data mais recente primeiro
        items = sorted(
            response.get("Items", []),
            key=lambda x: x.get("createdAt", ""),
            reverse=True
        )

        return success(200, items)

    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")