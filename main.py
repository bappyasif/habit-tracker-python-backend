import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app:server",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )


# uvicorn src.app:server --host 0.0.0.0 --port 8000 --reload --log-level debug