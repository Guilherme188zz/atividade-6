import json
import uuid
from datetime import datetime, timezone

import boto3
import os
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from src.shared.db import get_table
from src.shared.response import success, error


def get_history_table():
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ["HISTORY_TABLE_NAME"]
    return dynamodb.Table(table_name)


def handler(event, context):
    """
    PATCH /inventory/{id}/adjust
    Ajusta a quantidade em estoque de forma atômica
    e registra no histórico.
    """
    try:
        item_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body") or "{}")

        operation = body.get("operation")
        amount = body.get("amount")

        if operation not in ("add", "remove"):
            return error(400, "'operation' deve ser 'add' ou 'remove'")

        if not isinstance(amount, int) or amount <= 0:
            return error(400, "'amount' deve ser um inteiro positivo")

        table = get_table("TABLE_NAME")
        existing = table.get_item(Key={"id": item_id}).get("Item")
        if not existing:
            return error(404, f"Item com id '{item_id}' não encontrado")

        now = datetime.now(timezone.utc).isoformat()
        qty_before = int(existing["quantity"])

        if operation == "add":
            response = table.update_item(
                Key={"id": item_id},
                UpdateExpression="SET quantity = quantity + :amount, updatedAt = :now",
                ExpressionAttributeValues={
                    ":amount": amount,
                    ":now":    now,
                },
                ReturnValues="ALL_NEW",
            )
        else:
            try:
                response = table.update_item(
                    Key={"id": item_id},
                    UpdateExpression="SET quantity = quantity - :amount, updatedAt = :now",
                    ConditionExpression=Attr("quantity").gte(amount),
                    ExpressionAttributeValues={
                        ":amount": amount,
                        ":now":    now,
                    },
                    ReturnValues="ALL_NEW",
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                    return error(
                        400,
                        f"Estoque insuficiente. Quantidade atual: {qty_before}. "
                        f"Tentativa de remover: {amount}."
                    )
                raise

        updated_item = response["Attributes"]
        updated_item["quantity"]    = int(updated_item["quantity"])
        updated_item["minQuantity"] = int(updated_item["minQuantity"])
        qty_after = updated_item["quantity"]

        # Registra no histórico
        history_table = get_history_table()
        history_table.put_item(Item={
            "id":        str(uuid.uuid4()),
            "itemId":    item_id,
            "itemName":  existing["name"],
            "operation": operation,
            "amount":    amount,
            "qtyBefore": qty_before,
            "qtyAfter":  qty_after,
            "createdAt": now,
        })

        return success(200, updated_item)

    except json.JSONDecodeError:
        return error(400, "Body da requisição não é um JSON válido")
    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")