from src.shared.db import get_table
from src.shared.response import success, error
 
def handler(event, context):
    try:
        pet_id = event["pathParameters"]["id"]
        get_table().delete_item(Key={'id': pet_id})
        return success(200, {'message': 'Pet removido', 'id': pet_id})
    except Exception as e:
        print(f"Erro: {e}")
        return error(500, "Erro interno")
