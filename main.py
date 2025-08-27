from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from gmail_utils import fetch_emails_from_query
from gemini_agent import build_gmail_search_query, summarize_emails_with_query

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

class UserQuery(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat_with_gmail")
def chat_with_gmail(user_input: UserQuery):
    gmail_query = build_gmail_search_query(user_input.query)
    snippets = fetch_emails_from_query(gmail_query)
    result = summarize_emails_with_query(user_input.query, snippets)
    return {"answer": result}
