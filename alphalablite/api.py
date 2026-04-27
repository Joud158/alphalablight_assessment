from __future__ import annotations 
from fastapi import FastAPI, HTTPException, Query 
from pydantic import BaseModel, Field 
from .exceptions import AlphaLabLiteError, NotFoundError
from .serialization import encode_variables
from .service import AlphaLabLiteService

app = FastAPI(title="AlphaLabLite", version="1.0.0")
service = AlphaLabLiteService()

class ExecuteRequest(BaseModel):
    script: str = Field(..., min_length=1)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/execute")
def execute(request: ExecuteRequest) -> dict[str, str]:
    try:
        script_id = service.execute(request.script)
    except AlphaLabLiteError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Script successfully executed", "result": script_id}

@app.get("/view/{script_id}")
def view(script_id: str, items: list[str] = Query(...)) -> dict[str, list[float | None]]:
    try:
        result = service.view(script_id, items)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AlphaLabLiteError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return encode_variables(result)