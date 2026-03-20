from src.shared.db import get_table
from src.shared.response import success, error


def handler(event, context):
    """
    GET /inventory/{id}
    Busca um item de estoque pelo seu ID.
    """
    try:
        # O {id} da URL vem dentro de pathParameters
        item_id = event["pathParameters"]["id"]

        table = get_table("TABLE_NAME")
        response = table.get_item(Key={"id": item_id})

        item = response.get("Item")
        if not item:
            return error(404, f"Item com id '{item_id}' não encontrado")

        return success(200, item)

    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")