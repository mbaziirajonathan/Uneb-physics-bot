# main.py
from fastapi import FastAPI, Response, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from ai_logic import get_client, generate_ai_response
from database import get_session, save_session, log_activity
import traceback
import time

app = FastAPI(title="UCE Tutor WhatsApp API v1.0")
client = get_client()

ADMIN_NUMBER = "256751040731" # YOUR WHATSAPP NUMBER

# Rate limiting: prevent 1 student from spamming
LAST_REQUEST = {}

def is_rate_limited(phone: str, seconds=3):
    now = time.time()
    if phone in LAST_REQUEST and now - LAST_REQUEST[phone] < seconds:
        return True
    LAST_REQUEST[phone] = now
    return False

# TWILIO SENDS: From, Body, To
class TwilioWebhook(BaseModel):
    From: str
    Body: str
    To: str

@app.post("/webhook", response_class=PlainTextResponse)
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    This endpoint accepts both Twilio form-data and JSON
    Returns plain text that Twilio sends back to WhatsApp
    """
    try:
        # 1. Parse Twilio form data OR JSON
        form = await request.form()
        from_number = form.get("From", "").replace("whatsapp:", "") # whatsapp:+2567...
        message = form.get("Body", "")

        # Fallback for JSON testing
        if not from_number:
            data = await request.json()
            from_number = data.get("from_number", "")
            message = data.get("message", "")

        if not from_number or not message:
            return "Please send a message"

        # 2. Rate limit check
        if is_rate_limited(from_number):
            return "⚡ Please wait 3 seconds before sending another message"

        # 3. Parse subject/class from message. Ex: "bio s2 photosynthesis"
        subject, class_level, clean_message = parse_command(message)

        # 4. Run AI in background so webhook responds fast < 2s
        background_tasks.add_task(process_message, from_number, clean_message, subject, class_level)

        # 5. Immediate ack to Twilio
        return "🤖 UCE Tutor is typing..."

    except Exception as e:
        print(f"[ERROR] {traceback.format_exc()}")
        log_activity("SYSTEM", "ERROR", "ERROR", f"Webhook crash: {e}")
        return "Sorry, we had an error. Please try again. Admin has been notified."

def parse_command(message: str):
    """Parse 'bio s2 photosynthesis' -> Biology, S2, photosynthesis"""
    msg_lower = message.lower()
    subject = "Biology" # default
    class_level = "S4" # default

    if "physics" in msg_lower or msg_lower.startswith("phy"): subject = "Physics"
    elif "chemistry" in msg_lower or msg_lower.startswith("chem"): subject = "Chemistry"
    elif "biology" in msg_lower or msg_lower.startswith("bio"): subject = "Biology"

    for i in ["S1","S2","S3","S4"]:
        if i.lower() in msg_lower: class_level = i; break

    # Remove subject/class from message
    clean_message = message.replace(subject, "").replace(class_level, "").strip()
    if not clean_message: clean_message = message # if user only typed "bio s2"
    return subject, class_level, clean_message

def process_message(from_number, message, subject, class_level):
    """This runs in background so we don't timeout Twilio 15s limit"""
    try:
        user_id = from_number
        print(f"[ADMIN {ADMIN_NUMBER}] Received from {user_id}: {message}")

        # 1. Load history
        chat_history, activities_log = get_session(user_id, subject, class_level)

        # 2. Build prompt with context
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-6:]])
        full_prompt = f"History:\n{history_text}\n\nNew Question: {message}"

        # 3. Get AI Response
        ai_reply = generate_ai_response(client, full_prompt, subject, class_level)

        # 4. Save to DB
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": ai_reply})
        save_session(user_id, subject, class_level, chat_history, activities_log)
        log_activity(user_id, subject, class_level, f"WhatsApp: {message}")

        # 5. TODO: Here you call Twilio API to send `ai_reply` back to `from_number`
        # For now we just log it. Twilio will auto-reply with the first "typing..." response
        print(f"[SEND TO {from_number}]: {ai_reply}")

    except Exception as e:
        print(f"[PROCESS ERROR] {traceback.format_exc()}")
        log_activity(from_number, subject, class_level, f"AI Error: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "admin": ADMIN_NUMBER, "version": "1.0.0"}
