from src.shared.db import get_table
from src.shared.response import success, error
 
def handler(event, context):
    try:
        pet_id = event["pathParameters"]["id"]
        result = get_table().get_item(Key={'id': pet_id})
        pet = result.get("Item")
        if not pet:
            return error(404, "Pet não encontrado")
        return success(200, pet)
    except Exception as e:
        print(f"Erro: {e}")
        return error(500, "Erro interno")
