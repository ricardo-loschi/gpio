import requests
import json

header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic NGZhOTBiNWYtMzMyZC00ZjRkLWFhOTMtOGQ2ZGFkZDA1ZTAy"}

payload = {"app_id": "da410000-4f23-47e5-890e-f22beb3859cb",
           "included_segments": ["All"],
           "contents": {"en": "Alarme disparado!!"}}
 
req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
 
print(req.status_code, req.reason)
