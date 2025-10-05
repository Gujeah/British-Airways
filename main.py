from fastapi import FastAPI
from enum import Enum

app =FastAPI() 

@app.get("/predict")
async def predict():
    return "hello"