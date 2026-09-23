from fastapi import FastAPI
from .api import router

app = FastAPI(title="Mini Device Fleet Monitor", version="1.0.0")
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
