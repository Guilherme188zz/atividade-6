import json
import uuid
from datetime import datetime, timezone

from src.shared.db import get_table
from src.shared.response import success, error


def handler(event, context):
    """
    POST /inventory
    Cadastra um novo item no estoque da clínica.
    """
    try:
        body = json.loads(event.get("body") or "{}")

        # Valida campos obrigatórios
        required_fields = ["name", "category", "quantity", "unit", "minQuantity"]
        for field in required_fields:
            if field not in body:
                return error(400, f"Campo obrigatório ausente: '{field}'")

        # Valida categoria
        valid_categories = ["medication", "vaccine", "supply", "equipment"]
        if body["category"] not in valid_categories:
            return error(
                400,
                f"Categoria inválida. Use: {', '.join(valid_categories)}"
            )

        # Valida tipos numéricos
        if not isinstance(body["quantity"], int) or body["quantity"] < 0:
            return error(400, "'quantity' deve ser um inteiro maior ou igual a 0")
        if not isinstance(body["minQuantity"], int) or body["minQuantity"] < 0:
            return error(400, "'minQuantity' deve ser um inteiro maior ou igual a 0")

        now = datetime.now(timezone.utc).isoformat()

        item = {
            "id":          str(uuid.uuid4()),
            "name":        body["name"],
            "category":    body["category"],
            "quantity":    body["quantity"],
            "unit":        body["unit"],
            "minQuantity": body["minQuantity"],
            "createdAt":   now,
            "updatedAt":   now,
        }

        # Campos opcionais
        for field in ["supplier", "expiresAt", "unitCost"]:
            if field in body:
                item[field] = body[field]

        table = get_table()
        table.put_item(Item=item)

        return success(201, item)

    except json.JSONDecodeError:
        return error(400, "Body da requisição não é um JSON válido")
    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")