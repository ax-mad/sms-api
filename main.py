from pykit.logging import Logger
from fastapi    import FastAPI, Request, Form  # type: ignore
import httpx
import urllib.parse

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
    ToCity: str = Form(default=""),
    ToState: str = Form(default=""),
    ToCountry: str = Form(default=""),
    NumMedia: str = Form(default="0"),
    SmsSid: str = Form(default=""),
):
    # Decode the URL-encoded phone numbers
    from_num = urllib.parse.unquote(From)
    to_num = urllib.parse.unquote(To)
    
    # Build location string
    location_parts = [p for p in [FromCity, FromState, FromCountry] if p]
    location = ", ".join(location_parts) if location_parts else "Unknown location"
    
    # Build the message
    title = f"📱 SMS from {from_num}"
    if location != "Unknown location":
        title += f" ({location})"
    
    message = Body or "(empty message)"
    
    # Add media indicator
    tags = ["sms", "phone"]
    if NumMedia != "0":
        tags.append("paperclip")
        message += f"\n\n📎 {NumMedia} attachment(s)"
    
    # Priority: high for urgent words
    priority = 4 if any(word in Body.lower() for word in ["urgent", "asap", "emergency", "now"]) else 3
    
    ntfy_payload = {
        "topic": "sms",
        "message": message,
        "title": title,
        "tags": tags,
        "priority": priority,
        "actions": [
            {
                "action": "view",
                "label": "Reply",
                "url": f"https://wa.me/{from_num.replace('+', '')}"
            }
        ]
    }
    
    # Send to ntfy
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://ntfy.alj.cx/sms?auth=QmVhcmVyIHRrX3F5YjVzNzJra2ptMDVyYXJzaG52Mjc5am1oemxvCg",  # PUBLIC_TOKEN EXPIRTES IN 3 DAYS
            json=ntfy_payload
        )
        response.raise_for_status()
    
    return {"status": "forwarded", "message_sid": SmsSid}
