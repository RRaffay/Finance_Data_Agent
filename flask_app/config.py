import os


class Config:
    UPLOAD_FOLDER = 'uploads'
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_PROJECT = os.getenv(
        "LANGCHAIN_PROJECT", "Finance Agent")
