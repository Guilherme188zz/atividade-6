from boto3.dynamodb.conditions import Attr

from src.shared.db import get_table
from src.shared.response import success, error


def handler(event, context):
    """
    GET /inventory
    GET /inventory?category=medication
    GET /inventory?low_stock=true
    """
    try:
        params = event.get("queryStringParameters") or {}

        category  = params.get("category")
        low_stock = params.get("low_stock", "").lower() == "true"

        table = get_table()

        if low_stock:
            # Retorna só itens onde quantity <= minQuantity
            response = table.scan(
                FilterExpression=Attr("quantity").lte(Attr("minQuantity"))
            )
        elif category:
            # Filtra por categoria exata
            response = table.scan(
                FilterExpression=Attr("category").eq(category)
            )
        else:
            # Sem filtro — retorna tudo
            response = table.scan()

        items = response.get("Items", [])
        return success(200, items)

    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")