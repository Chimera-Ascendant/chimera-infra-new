import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from .schemas import InferenceRequest, InferenceResponse
from .rules_engine import decide

app = FastAPI(title="Chimera Cognitive Core", version="0.1.0")

API_TOKEN = os.getenv("CHIMERA_API_TOKEN")

@app.post("/cognitive-core/infer", response_model=InferenceResponse)
async def cognitive_infer(req: InferenceRequest, authorization: Optional[str] = Header(None)):
    # Optional Bearer auth; enforced only if env token is set
    if API_TOKEN:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing bearer token")
        token = authorization.split(" ", 1)[1].strip()
        if token != API_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid token")

    result = decide(req)
    return JSONResponse(content=result)
