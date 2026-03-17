from src.shared.db import get_table
from src.shared.response import success, error
 
def handler(event, context):
    try:
        result = get_table().scan()
        pets = sorted(result.get("Items", []),
            key=lambda x: x.get("createdAt", ""), reverse=True)
        return success(200, pets)
    except Exception as e:
        print(f"Erro: {e}")
        return error(500, "Erro interno")
