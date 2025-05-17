"""Ultra minimal app - health check only"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "alive"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
