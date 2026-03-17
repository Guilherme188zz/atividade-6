import json
from datetime import datetime
from src.shared.db import get_table
from src.shared.response import success, error
 
def handler(event, context):
    try:
        pet_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body", "{}"))
        table = get_table()
 
        table.update_item(
            Key={'id': pet_id},
            UpdateExpression='SET #n=:n, species=:s, breed=:b, ownerName=:o, ownerPhone=:p, updatedAt=:u',
            ExpressionAttributeNames={'#n': 'name'},
            ExpressionAttributeValues={
                ':n': body.get('name', ''),
                ':s': body.get('species', ''),
                ':b': body.get('breed', ''),
                ':o': body.get('ownerName', ''),
                ':p': body.get('ownerPhone', ''),
                ':u': datetime.utcnow().isoformat()
            }
        )
        return success(200, {'id': pet_id, 'updated': True})
    except Exception as e:
        print(f"Erro: {e}")
        return error(500, "Erro interno")
