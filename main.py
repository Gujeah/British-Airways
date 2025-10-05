from fastapi import FastAPI,Form, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from enum import Enum
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from predict import predict_recommendation
from database import db_init, save_feedback, get_all_feedback
from fastapi.staticfiles import StaticFiles

### we need to initialize our database
db_init()

app =FastAPI() 
analyzer=SentimentIntensityAnalyzer()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates=Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def show_form(request:Request):
    return templates.TemplateResponse(
        "review_form.html", 
        {"request":request, "submitted":False}
        )
    

@app.post("/submit_review")
async def handle_review(request: Request,review_text:str = Form(...)):
    result=predict_recommendation(review_text)

    ### saving our review to our database
    save_feedback( 
        review_text=review_text,
        is_likely=result["is_likely"],
        confidence=result["confidence"]
        )
    return templates.TemplateResponse("review_form.html", {
        "request": request,
        "submitted": True
    })
    
