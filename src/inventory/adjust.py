import json
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from src.shared.db import get_table
from src.shared.response import success, error


def handler(event, context):
    """
    PATCH /inventory/{id}/adjust
    Ajusta a quantidade em estoque de forma atômica.

    Body esperado:
      { "operation": "add" | "remove", "amount": 10 }
    """
    try:
        item_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body") or "{}")

        # Valida os campos do body
        operation = body.get("operation")
        amount = body.get("amount")

        if operation not in ("add", "remove"):
            return error(400, "'operation' deve ser 'add' ou 'remove'")

        if not isinstance(amount, int) or amount <= 0:
            return error(400, "'amount' deve ser um inteiro positivo")

        # Verifica se o item existe
        table = get_table()
        existing = table.get_item(Key={"id": item_id}).get("Item")
        if not existing:
            return error(404, f"Item com id '{item_id}' não encontrado")

        now = datetime.now(timezone.utc).isoformat()

        if operation == "add":
            # Incremento atômico — quantity = quantity + amount
            response = table.update_item(
                Key={"id": item_id},
                UpdateExpression="SET quantity = quantity + :amount, updatedAt = :now",
                ExpressionAttributeValues={
                    ":amount": amount,
                    ":now":    now,
                },
                ReturnValues="ALL_NEW",
            )

        else:  # operation == "remove"
            try:
                # Só executa se quantity >= amount (proteção contra negativo)
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
                    current_qty = existing["quantity"]
                    return error(
                        400,
                        f"Estoque insuficiente. Quantidade atual: {current_qty}. "
                        f"Tentativa de remover: {amount}."
                    )
                raise

        updated_item = response["Attributes"]
        return success(200, updated_item)

    except json.JSONDecodeError:
        return error(400, "Body da requisição não é um JSON válido")
    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")
