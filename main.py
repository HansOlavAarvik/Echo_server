from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
#from typing import List, Optional
#import pandas as pd
import time
import threading
import database
from div import log
import dashboard
from UDP_recieve import UDP_main

app = FastAPI(title="ECHO Monitor API")

udp_thread = None

@app.on_event("startup")
async def startup_event():
    global udp_thread
    log("Starting UDP receiver thread...")
    udp_thread = threading.Thread(target=UDP_main, daemon=True)
    udp_thread.start()
    # Allow some time for the UDP thread to initialize
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

