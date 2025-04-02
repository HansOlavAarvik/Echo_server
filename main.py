from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
#from typing import List, Optional
#import pandas as pd
import time
import threading

import dashboard
from UDP_recieve import UDP_main

app = FastAPI(title="ECHO Monitor API")



udp_thread = threading.Thread(target=UDP_main, daemon=True)
udp_thread.start()

@app.get("/")
def read_root():
    return {"status": "ECHO Monitor API is running"}


app.mount("/dashboard", WSGIMiddleware(dashboard.server))
# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

