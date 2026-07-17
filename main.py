# main.py
from fastapi import FastAPI, Response, Request
from pydantic import BaseModel
from ai_logic import get_client, generate_ai_response
from database import get_session, save_session, log_activity
import os

app = FastAPI(title="UCE Tutor WhatsApp API")
client = get_client()

ADMIN_NUMBER = "256751040731" # YOUR WHATSAPP NUMBER

# This is what Twilio/WhatsApp Cloud API will POST to
class IncomingMessage(BaseModel):
    from_number: str # Student's number e.g. 256772123456
    message: str
    subject: str = "Biology" # Default. Later we can parse "bio: topic" from message
    class_level: str = "S4"

@app.post("/webhook")
async def webhook(msg: IncomingMessage):
    user_id = msg.from_number # KEY: Each student is separated by phone number
    user_message = msg.message
    subject = msg.subject
    class_level = msg.class_level

    # 1. Log that admin 256751040731 received a message
    print(f"[ADMIN {ADMIN_NUMBER}] Received from {user_id}: {user_message}")

    # 2. Load this student's history from DB
    chat_history, activities_log = get_session(user_id, subject, class_level)

    # 3. Build prompt with last 6 messages for context
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-6:]])
    full_prompt = f"History:\n{history_text}\n\nNew Question: {user_message}"

    # 4. Get AI Response from your brain
    ai_reply = generate_ai_response(client, full_prompt, subject, class_level)

    # 5. Save back to DB
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": ai_reply})
    save_session(user_id, subject, class_level, chat_history, activities_log)
    log_activity(user_id, subject, class_level, f"WhatsApp: {user_message}")

    # 6. Return plain text. Twilio/Yo will send this back to the student
    return Response(content=ai_reply, media_type="text/plain")

@app.get("/health")
def health(): 
    return {"status": "ok", "admin": ADMIN_NUMBER}

# BONUS: Admin endpoint to broadcast to all students
@app.post("/admin/broadcast")
async def broadcast(request: Request):
    data = await request.json()
    message = data.get("message")
    # TODO: Loop all user_ids in DB and send message
    print(f"[ADMIN {ADMIN_NUMBER} BROADCAST]: {message}")
    return {"status": "sent", "from": ADMIN_NUMBER}
