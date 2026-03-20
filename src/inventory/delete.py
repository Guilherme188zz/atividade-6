from src.shared.db import get_table
from src.shared.response import success, error


def handler(event, context):
    """
    DELETE /inventory/{id}
    Remove um item de estoque pelo ID.
    """
    try:
        item_id = event["pathParameters"]["id"]
        table = get_table("TABLE_NAME")

        # Verifica se existe antes de deletar
        existing = table.get_item(Key={"id": item_id}).get("Item")
        if not existing:
            return error(404, f"Item com id '{item_id}' não encontrado")

        table.delete_item(Key={"id": item_id})

        return success(200, {"message": f"Item '{item_id}' removido com sucesso"})

    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")