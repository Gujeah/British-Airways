from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import JSONResponse,HTMLResponse,StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from enum import Enum
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from predict import predict_recommendation
from database import db_init, save_feedback, get_all_feedback
from fastapi.staticfiles import StaticFiles
import csv
import io

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
    
admin_password="ethel" ##have just added this
### now we should work on our admin panel 
@app.get("/admin", response_class=HTMLResponse)
async def admin_log_in_form(request:Request):
    return templates.TemplateResponse("admin_login.html", {"request":request})


@app.post("/admin/login")
async def admin_login(request: Request, password: str = Form(...)):
    if password == admin_password:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_auth", value="true")
        return response
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "error": "Invalid password"
    })
def require_auth(request:Request):
    if request.cookies.get("admin_auth")!="true":
        raise HTTPException(status_code=403, detail="Not authorized")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request:Request):
    require_auth(request)
    feedback=get_all_feedback()
    total=len(feedback)
    promoters=sum(1 for f in feedback if f["is_likely"])
    nps_percent = (promoters / total * 100) if total > 0 else 0
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "feedback": feedback,
        "total": total,
        "promoters": promoters,
        "nps_percent": round(nps_percent, 1)
    })

@app.get("/admin/export/csv")
async def export_csv(request: Request):
    require_auth(request)
    feedback = get_all_feedback()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp", "Review", "Likely to Recommend", "Confidence"])
    for fb in feedback:
        writer.writerow([
            fb["id"],
            fb["timestamp"],
            fb["review_text"],
            "Yes" if fb["is_likely"] else "No",
            fb["confidence"]
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=feedback_export.csv"}
    )