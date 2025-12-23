from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()
security = HTTPBasic()


CLIENT_KEY = "dckey_EHldkoRCUGXGtPDc5ufEArLuoJvxoroM"
SECRET_KEY = "dskey_RyK-Y5-z4oz_Ju_QhAHDOsA_W7bm7ejd"


mongo = MongoClient("mongodb://localhost:27017")
db = mongo["ipospay_local"]
collection = db["ipos_feed_log"]


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username.strip()
    password = credentials.password.strip()

    if username != CLIENT_KEY or password != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return True


@app.post("/ipos/feeds/webhook")
async def ipos_webhook(request: Request, auth=Depends(check_auth)):
    try:
        body = await request.body()
        body_text = body.decode("utf-8", errors="ignore")

        data = {
            "headers": dict(request.headers),
            "body": body_text,
            "received_at": datetime.utcnow()
        }

        collection.insert_one(data)

        return {"status": "ok", "message": "Saved log data"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
