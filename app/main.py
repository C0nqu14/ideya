from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.ideya import router as ideya_router

app = FastAPI(title="Ideya API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/" , tags=["index" , "home"])
def initial_page():
    raise HTTPException(status_code=status.HTTP_200_OK , detail="API ON")

app.include_router(ideya_router, tags=["ideya"])
