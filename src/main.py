from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from .api import router, store
from .logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")
    store.close()

app = FastAPI(title="Mini Device Fleet Monitor", version="1.0.0", lifespan=lifespan)
app.include_router(router)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
