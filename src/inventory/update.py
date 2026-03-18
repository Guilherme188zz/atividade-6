import json
from datetime import datetime, timezone

from src.shared.db import get_table
from src.shared.response import success, error


def handler(event, context):
    """
    PUT /inventory/{id}
    Atualiza completamente um item de estoque.
    """
    try:
        item_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body") or "{}")

        # Verifica se o item existe antes de atualizar
        table = get_table()
        existing = table.get_item(Key={"id": item_id}).get("Item")
        if not existing:
            return error(404, f"Item com id '{item_id}' não encontrado")

        # Valida campos obrigatórios
        required_fields = ["name", "category", "quantity", "unit", "minQuantity"]
        for field in required_fields:
            if field not in body:
                return error(400, f"Campo obrigatório ausente: '{field}'")

        # Valida categoria
        valid_categories = ["medication", "vaccine", "supply", "equipment"]
        if body["category"] not in valid_categories:
            return error(400, f"Categoria inválida. Use: {', '.join(valid_categories)}")

        # Valida tipos numéricos
        if not isinstance(body["quantity"], int) or body["quantity"] < 0:
            return error(400, "'quantity' deve ser um inteiro maior ou igual a 0")
        if not isinstance(body["minQuantity"], int) or body["minQuantity"] < 0:
            return error(400, "'minQuantity' deve ser um inteiro maior ou igual a 0")

        now = datetime.now(timezone.utc).isoformat()

        updated_item = {
            "id":          item_id,
            "name":        body["name"],
            "category":    body["category"],
            "quantity":    body["quantity"],
            "unit":        body["unit"],
            "minQuantity": body["minQuantity"],
            "createdAt":   existing["createdAt"],  # preserva o original!
            "updatedAt":   now,
        }

        # Campos opcionais
        for field in ["supplier", "expiresAt", "unitCost"]:
            if field in body:
                updated_item[field] = body[field]

        table.put_item(Item=updated_item)

        return success(200, updated_item)

    except json.JSONDecodeError:
        return error(400, "Body da requisição não é um JSON válido")
    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")