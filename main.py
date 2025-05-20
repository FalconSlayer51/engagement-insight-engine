from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

@app.get('/health')
def health():
    return {'status': "ok"}

@app.get('/version')
def version():
    return { 'version': '1.0.0'}
