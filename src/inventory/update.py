import json
from datetime import datetime, timezone

from src.shared.db import get_table
from src.shared.response import success, error


def validate_date(date_str):
    """Valida se a string é uma data ISO 8601 válida."""
    try:
        datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def handler(event, context):
    """
    PUT /inventory/{id}
    Atualiza completamente um item de estoque.
    """
    try:
        item_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body") or "{}")

        # Verifica se o item existe
        table = get_table("TABLE_NAME")
        existing = table.get_item(Key={"id": item_id}).get("Item")
        if not existing:
            return error(404, f"Item com id '{item_id}' não encontrado")

        # Valida campos obrigatórios
        required_fields = ["name", "category", "quantity", "unit", "minQuantity", "expiresAt", "unitCost"]
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

        # Valida data de validade
        if not validate_date(body["expiresAt"]):
            return error(400, "'expiresAt' deve ser uma data válida no formato ISO 8601. Ex: 2026-12-31T00:00:00Z")

        # Valida unitCost
        if not isinstance(body["unitCost"], (int, float)) or body["unitCost"] < 0:
            return error(400, "'unitCost' deve ser um número maior ou igual a 0")

        now = datetime.now(timezone.utc).isoformat()

        updated_item = {
            "id":          item_id,
            "name":        body["name"],
            "category":    body["category"],
            "quantity":    body["quantity"],
            "unit":        body["unit"],
            "minQuantity": body["minQuantity"],
            "expiresAt":   body["expiresAt"],
            "unitCost":    body["unitCost"],
            "createdAt":   existing["createdAt"],
            "updatedAt":   now,
        }

        # Campo opcional
        if "supplier" in body:
            updated_item["supplier"] = body["supplier"]

        table.put_item(Item=updated_item)

        return success(200, updated_item)

    except json.JSONDecodeError:
        return error(400, "Body da requisição não é um JSON válido")
    except Exception as e:
        return error(500, f"Erro interno: {str(e)}")