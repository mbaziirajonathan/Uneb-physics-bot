# local_llm_server.py
# Run with: python local_llm_server.py
# Requires: pip install fastapi uvicorn llama-cpp-python zeroconf pydantic

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_cpp import Llama
from zeroconf import ServiceInfo, Zeroconf
import socket
import threading
import os

app = FastAPI(title="UNEB Local LLM Edge Server Phi3", version="1.1.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. HARDCODED PATH TO YOUR MODEL
MODEL_PATH = r"C:\unebserver\models\Phi-3-mini-4k-instruct-q4.gguf"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

print(f"Loading Phi3 from: {MODEL_PATH}... This takes 20-40s")
llm = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=-1, # -1 = use all GPU VRAM. Set 0 for CPU only
    n_ctx=4096, # Phi3 4k context
    n_threads=os.cpu_count(), # Use all CPU cores
    verbose=False
)
print("Phi3 Loaded and Ready on http://0.0.0.0:8000")

class ChatRequest(BaseModel):
    messages: list
    temperature: float = 0.1
    max_tokens: int = 1600

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    try:
        # Convert OpenAI messages to Phi3 ChatML format
        prompt = ""
        for msg in req.messages:
            if msg["role"] == "system": prompt += f"<|system|>\n{msg['content']}<|end|>\n"
            elif msg["role"] == "user": prompt += f"<|user|>\n{msg['content']}<|end|>\n"
            elif msg["role"] == "assistant": prompt += f"<|assistant|>\n{msg['content']}<|end|>\n"
        prompt += "<|assistant|>\n"

        output = llm(
            prompt,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            stop=["<|end|>", "<|user|>", "<|system|>"],
            echo=False
        )
        content = output["choices"][0]["text"].strip()
        return {"message": {"role": "assistant", "content": content}}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/health")
def health():
    return {"status": "ok", "model": "Phi-3-mini-4k-instruct-q4.gguf"}

# 2. AUTO DISCOVERY: Broadcast as uneb-tutor-local.local
def register_mdns():
    ip = socket.gethostbyname(socket.gethostname())
    info = ServiceInfo(
        "_http._tcp.local.",
        "uneb-tutor-local._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=8000,
        properties={'version': '1.1.3'},
        server="uneb-tutor-local.local.",
    )
    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    print(f"mDNS: Registered as uneb-tutor-local.local:8000 at IP {ip}")

if __name__ == "__main__":
    threading.Thread(target=register_mdns, daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
