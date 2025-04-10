from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
import time
import threading
import database
from div import log
import Frontend.dashboard as dashboard
from UDP_recieve import UDP_main_json, UDP_main_audio
from audio_API import router as audio_router


app = FastAPI(title="ECHO Monitor API")
app.include_router(audio_router)

udp_json_thread = None
udp_audio_thread = None

@app.on_event("startup")
async def startup_json_receiver():
    global udp_json_thread
    log("Starting UDP receiver thread...")
    udp_json_thread = threading.Thread(target=UDP_main_json, daemon=True)
    udp_json_thread.start()
    time.sleep(0.5) 
@app.on_event("startup")
async def startup_audio_reciever():
    global udp_json_thread
    log("Starting UDP receiver thread...")
    udp_json_thread = threading.Thread(target=UDP_main_audio, daemon=True)
    udp_json_thread.start()
    time.sleep(0.5)


@app.get("/")
def read_root():
    return {"status": "ECHO Monitor API is running"}

@app.get("/data-status")
def data_status():
    df = database.recent_data()
    return {
        "rows": len(df),
        "columns": list(df.columns) if not df.empty else []
    }

app.mount("/dashboard", WSGIMiddleware(dashboard.server))
# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

