from fastapi import FastAPI
from starlette.config import Config

config = Config(".env")


app = FastAPI()
