from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()
security = HTTPBasic()


CLIENT_KEY = "9FvQ3KxA7M2pR5WcLZ8HnE4TBydU"
SECRET_KEY = "S3cr3t!@#A9xPqL7D2MZK8W$R4EJHfYtC"


mongo = MongoClient("mongodb://localhost:27017")
db = mongo["ipospay_local"]
collection = db["ipos_feed_log"]


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != CLIENT_KEY or credentials.password != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


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
