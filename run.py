from app.main import app

if __name__ == "__main__":
    import uvicorn

    # uvicorn app.main:app --port 8000 --host
    uvicorn.run("app.main:app", host="0.0.0.0", port=80, reload=True)
