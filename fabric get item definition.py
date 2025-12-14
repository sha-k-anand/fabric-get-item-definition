from datetime import datetime,timedelta
import requests
import base64
import json
import os
from typing import Dict, Any

def decode_payload_to_json(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    decoded_parts = {}
    
    for part in input_payload["definition"]["parts"]:
        path = part["path"]
        base64_payload = part["payload"]
        
        # Decode base64 to string
        decoded_bytes = base64.b64decode(base64_payload)
        decoded_content = decoded_bytes.decode("utf-8")
        
        # Try to parse as JSON and pretty-print if possible
        try:
            json_obj = json.loads(decoded_content)
            decoded_parts[path] = json_obj  # Store as Python dict (will become JSON when dumped)
        except json.JSONDecodeError:
            # Not JSON (e.g., Power Query M code), store as raw string
            decoded_parts[path] = decoded_content
    
    # Return a clean JSON-serializable structure
    return {
        "decoded_parts": decoded_parts
    }



client_id = ""
client_secret = ""
tenant_id = ""

token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "https://analysis.windows.net/powerbi/api/.default",
}


response = requests.post(token_url, headers=headers, data=data)
token = response.json()["access_token"]

workspaceguid = ["8b159f43-b843-4c04-99bc-a0f320c9ebf5","f7d49bae-aafc-42fa-ae29-8fe87e570982"]
headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
for wsguid in workspaceguid:
    #gets only DF gen2 cicd, not Gen1 or Gen 2.0
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{wsguid}/items"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        errormessage =  f"Access Issue  - workspace {wsguid}"
        print (errormessage)
    else:
        errormessage =  f"Collecting Inventory - workspace {wsguid}"
        print (errormessage)

        response_json = response.json()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
            }

        for item in response_json['value']:
            print(f"ID: {item['id']}, Type: {item['type']}, Display Name: {item['displayName']}")        
            if item['type'] in ["Dataflow","CopyJob"]:
                if item['type'] in ("Dataflow"):
                    itemtype = "Dataflow Gen 2 CICD"
                else:
                    itemtype = item['type']

                print(f"ID: {item['id']}, Type: {item['type']}, Display Name: {item['displayName']}")        

                url = f"https://api.fabric.microsoft.com/v1/workspaces/{wsguid}/items/{item['id']}/getDefinition"

                response = requests.post(url, headers=headers)
                #print(response.json())
                output_dir = "C:\\FabricItemInventory\\"
                output_filename = 'WS__' + wsguid + '__'+ item['id'] + '__' + item['displayName'] + '__' + item['type'] + '.json'
                filepath = os.path.join(output_dir, output_filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(response.json(), f, indent=4, ensure_ascii=False)

                output_filename = 'DecodedJSON_WS__' + wsguid + '__'+ item['id'] + '__' + item['displayName'] + '__' + item['type'] + '.json'
                filepath = os.path.join(output_dir, output_filename)
                decodedJSON_response = decode_payload_to_json(response.json())
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(decodedJSON_response, f, indent=4, ensure_ascii=False)



