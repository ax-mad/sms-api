from pykit.logging import Logger
from fastapi    import FastAPI, Request, Form  # type: ignore
import httpx
import urllib.parse
import json

log = Logger(name="uvicorn", color="magenta")
app = FastAPI(title="CalDAV API")

@app.get("/test")
def check_health():
    log("Health check")
    return {"status": "ok"}

@app.post("/sms")
async def receive_sms(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(default=""),
    FromCity: str = Form(default=""),
    FromState: str = Form(default=""),
    FromCountry: str = Form(default=""),
    NumMedia: str = Form(default="0"),
    SmsSid: str = Form(default=""),
):
    from_num = urllib.parse.unquote(From)
    
    # Build location
    location_parts = [p for p in [FromCity, FromState, FromCountry] if p]
    location = ", ".join(location_parts) if location_parts else "Unknown"
    
    # Build notification
    title = f"📱 {from_num}"
    if location != "Unknown":
        title += f" ({location})"
    
    message = Body or "(empty message)"
    tags = ["sms", "phone"]
    if NumMedia != "0":
        tags.append("paperclip")
    
    # ntfy payload - NO "topic" here since it's in the URL
    ntfy_payload = {
        "message": message,
        "title": title,
        "tags": tags,
        "priority": 3,
        "actions": [{
            "action": "view",
            "label": "Reply",
            "url": f"https://wa.me/{from_num.replace('+', '')}"
        }]
    }

    log("SMS RECEIVED")
    
    # Send as raw JSON string, not httpx's json= parameter
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://ntfy.alj.cx/sms?auth=QmVhcmVyIHRrX3F5YjVzNzJra2ptMDVyYXJzaG52Mjc5am1oemxvCg",
            content=json.dumps(ntfy_payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    
    return {"status": "forwarded", "message_sid": SmsSid}
