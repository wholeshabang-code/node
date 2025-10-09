from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import shutil
from typing import Optional

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/note/{uuid}", response_class=HTMLResponse)
async def get_note(request: Request, uuid: str, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.uuid == uuid).first()
    
    if not note:
        # Show attach content page if note doesn't exist
        return templates.TemplateResponse(
            "attach.html",
            {"request": request, "uuid": uuid}
        )
    
    if note.content_type == "url":
        return RedirectResponse(url=note.content)
    elif note.content_type == "image":
        return templates.TemplateResponse(
            "view.html",
            {"request": request, "note": note, "content_type": "image"}
        )
    else:  # text
        return templates.TemplateResponse(
            "view.html",
            {"request": request, "note": note, "content_type": "text"}
        )

@app.post("/note/{uuid}")
async def create_note(
    request: Request,
    uuid: str,
    content_type: str = Form(...),
    content: Optional[str] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    if content_type not in ["url", "text", "image"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
    
    if content_type == "image" and image:
        # Save the uploaded image
        file_path = f"static/images/{uuid}{os.path.splitext(image.filename)[1]}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        content = f"/static/images/{uuid}{os.path.splitext(image.filename)[1]}"
    elif not content and content_type != "image":
        raise HTTPException(status_code=400, detail="Content is required")
    
    note = models.Note(
        uuid=uuid,
        content_type=content_type,
        content=content
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return templates.TemplateResponse(
        "confirmation.html",
        {
            "request": request,
            "content_type": note.content_type,
            "content": note.content
        }
    )