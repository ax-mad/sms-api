from pykit.logging import Logger
from fastapi    import FastAPI, Request  # type: ignore

log = Logger(name="uvicorn", color="magenta")
app = FastAPI(title="CalDAV API")

@app.get("/test")
def check_health():
    log("Health check")
    return {"status": "ok", "message": "u good my boi"}

@app.post("/sms")
async def receive_sms(webhook: Request):
    body = await webhook.body()
    headers = dict(webhook.headers)
    
    log(f"Headers: {headers}")
    log(f"Body: {body.decode()}")
    
    return {}
