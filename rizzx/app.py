from __future__ import annotations
import secrets
import time
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

ROOT = Path(__file__).parent
app = FastAPI(title="RIZZ-X Remote Support")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

# In-memory sessions: intentionally disappear when the server stops.
sessions: Dict[str, dict] = {}
PIN_TTL = 600
SESSION_TTL = 1800

def now() -> float:
    return time.time()

def cleanup():
    for pin in list(sessions):
        s = sessions[pin]
        if now() - s["created"] > SESSION_TTL or (s.get("used") and now() - s["created"] > PIN_TTL):
            sessions.pop(pin, None)

@app.get("/", response_class=HTMLResponse)
async def home():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/health")
async def health():
    cleanup()
    return {"app": "RIZZ-X", "status": "ok", "active_sessions": len(sessions)}

@app.post("/api/create")
async def create_session(request: Request):
    cleanup()
    # PIN is a short-lived rendezvous code, not a substitute for HTTPS/VPN.
    for _ in range(20):
        pin = f"{secrets.randbelow(1_000_000):06d}"
        if pin not in sessions:
            break
    else:
        return JSONResponse({"error": "Could not create a session"}, status_code=503)
    sessions[pin] = {
        "created": now(), "host": None, "viewer": None, "used": False,
        "host_connected": False, "viewer_connected": False
    }
    return {"pin": pin, "expires_in_seconds": PIN_TTL}

@app.websocket("/ws/{pin}/{role}")
async def signaling(websocket: WebSocket, pin: str, role: str):
    cleanup()
    await websocket.accept()
    if role not in ("host", "viewer") or pin not in sessions:
        await websocket.send_json({"type": "error", "message": "Invalid or expired PIN."})
        await websocket.close(code=1008)
        return
    s = sessions[pin]
    if role == "viewer":
        if s["used"] or s["viewer_connected"]:
            await websocket.send_json({"type": "error", "message": "PIN already used."})
            await websocket.close(code=1008)
            return
        s["used"] = True
        s["viewer"] = websocket
        s["viewer_connected"] = True
    else:
        if s["host_connected"]:
            await websocket.send_json({"type": "error", "message": "Host already connected."})
            await websocket.close(code=1008)
            return
        s["host"] = websocket
        s["host_connected"] = True

    await websocket.send_json({"type": "ready", "role": role})
    other_role = "viewer" if role == "host" else "host"
    try:
        while True:
            message = await websocket.receive_json()
            # Only forward the WebRTC offer/answer/ICE and host-controlled state.
            if message.get("type") not in {"offer", "answer", "ice", "sharing", "stop"}:
                continue
            target = s.get(other_role)
            if target is not None:
                await target.send_json({"type": message["type"], "data": message.get("data")})
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        s[f"{role}_connected"] = False
        s[role] = None
        target = s.get(other_role)
        if target is not None:
            try:
                await target.send_json({"type": "peer_left"})
            except Exception:
                pass

def run():
    print("RIZZ-X running at http://127.0.0.1:8765")
    uvicorn.run("rizzx.app:app", host="0.0.0.0", port=8765, reload=False)

if __name__ == "__main__":
    run()
