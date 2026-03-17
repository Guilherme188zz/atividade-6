import json, uuid
from datetime import datetime
from src.shared.db import get_table
from src.shared.response import success, error
 
def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        name = body.get("name")
        species = body.get("species")
        owner_name = body.get("ownerName")
 
        if not all([name, species, owner_name]):
            return error(400, "Campos obrigatórios: name, species, ownerName")
 
        pet = {
            "id": str(uuid.uuid4()),
            "name": name,
            "species": species,
            "breed": body.get("breed"),
            "ownerName": owner_name,
            "ownerPhone": body.get("ownerPhone"),
            "createdAt": datetime.utcnow().isoformat()
        }
 
        get_table().put_item(Item=pet)
        return success(201, pet)
 
    except Exception as e:
        print(f"Erro: {e}")
        return error(500, "Erro interno")
