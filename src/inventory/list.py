from boto3.dynamodb.conditions import Attr

from src.shared.db import get_table
from src.shared.response import success, error


def fix_types(item):
    """Converte quantity e minQuantity para inteiro."""
    if "quantity" in item:
        item["quantity"] = int(item["quantity"])
    if "minQuantity" in item:
        item["minQuantity"] = int(item["minQuantity"])
    return item


def scan_all(table, **kwargs):
    """Faz scan completo lidando com paginação do DynamoDB."""
    items = []
    while True:
        response = table.scan(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key
    return items


def handler(event, context):
    """
    GET /inventory
    GET /inventory?category=medication
    GET /inventory?low_stock=true
    GET /inventory?expiring=true
    GET /inventory?name=amoxicilina
    """
    try:
        params = event.get("queryStringParameters") or {}
        category  = params.get("category")
        low_stock = params.get("low_stock", "").lower() == "true"
        expiring  = params.get("expiring", "").lower() == "true"
        name      = params.get("name", "").strip().lower()

        table = get_table("TABLE_NAME")

        if low_stock:
            items = scan_all(
                table,
                FilterExpression=Attr("quantity").lte(Attr("minQuantity"))
            )
        elif expiring:
            # Busca itens que têm expiresAt definido
            items = scan_all(
                table,
                FilterExpression=Attr("expiresAt").exists()
            )
            # Filtra no Python os que vencem em até 15 dias ou já venceram
            from datetime import datetime, timezone, timedelta
            now     = datetime.now(timezone.utc)
            limit   = now + timedelta(days=15)
            items = [
                i for i in items
                if i.get("expiresAt") and
                datetime.fromisoformat(i["expiresAt"].replace("Z", "+00:00")) <= limit
            ]
        elif category:
            items = scan_all(
                table,
                FilterExpression=Attr("category").eq(category)
            )
        elif name:
            # Busca por nome (contains, case-insensitive)
            items = scan_all(
                table,
                FilterExpression=Attr("name").contains(name)
            )
        else:
            items = scan_all(table)

        items = [fix_types(item) for item in items]
        return success(200, items)

    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")