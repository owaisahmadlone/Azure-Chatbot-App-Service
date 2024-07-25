from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import List,Optional
from modules import parse_pdf, chunk_text, upload_to_vector_db, generate_model_response
from models import Question,Answer
import os
from fastapi.middleware.cors import CORSMiddleware

# Global variables
pdf_uploaded = False
conversation_history = []
file_location = ""

def reset_chat_state():
    # Reset any necessary state for starting a new chat session
    global conversation_history,pdf_uploaded
    conversation_history = []
    pdf_uploaded = False


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
def index():
    return "Welcome to Mindcase Vault!!"

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    
    os.makedirs("./pdfs", exist_ok=True)
    file_location = f"./pdfs/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    text = parse_pdf(file_location)
    chunks = chunk_text(text)
    await upload_to_vector_db(chunks,file.filename)

    global pdf_uploaded,conversation_history
    pdf_uploaded = True
    conversation_history = []

    return {"filename": file.filename,"status": "uploaded"}

@app.post("/generate-response/",response_model = Answer)
async def generate_response(request: Question):
    print(pdf_uploaded)
    
    answer = await generate_model_response(request.question, conversation_history,pdf_uploaded)
    conversation_history.append(request.question)
    conversation_history.append(answer.answer)
    
    return answer

@app.get("/new-chat/")
async def new_chat():
    reset_chat_state()
    return {"status": "success", "message": "New chat session started"}

