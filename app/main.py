from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from typing import Optional
import logging
from datetime import datetime

from .supabase_client import get_supabase

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add error handler for 500 errors
@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception):
    logger.error(f"Internal Server Error: {exc}", exc_info=True)
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": str(exc)},
        status_code=500
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/note/{uuid}", response_class=HTMLResponse)
async def get_note(request: Request, uuid: str):
    try:
        logger.debug(f"Accessing note with UUID: {uuid}")
        supabase = get_supabase()
        
        try:
            response = supabase.table('notes').select('*').eq('uuid', uuid).execute()
            notes = response.data
            note = notes[0] if notes else None
            logger.debug(f"Database query successful. Note found: {note is not None}")
        except Exception as e:
            logger.error(f"Database error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        if not note:
            logger.debug(f"No note found for UUID {uuid}, showing attach form")
            return templates.TemplateResponse(
                "attach.html",
                {"request": request, "uuid": uuid}
            )
        
        logger.debug(f"Note found, type: {note['content_type']}, content: {note['content'][:100]}...")
        
        if note['content_type'] == "url":
            return RedirectResponse(url=note['content'])
        elif note['content_type'] == "image":
            return templates.TemplateResponse(
                "view.html",
                {"request": request, "note": note, "content_type": "image"}
            )
        else:  # text
            return templates.TemplateResponse(
                "view.html",
                {"request": request, "note": note, "content_type": "text"}
            )
    except Exception as e:
        logger.error(f"Error processing note {uuid}: {e}", exc_info=True)
        raise

@app.post("/note/{uuid}")
async def create_note(
    request: Request,
    uuid: str,
    content_type: str = Form(...),
    content: Optional[str] = Form(None),
    image: UploadFile = File(None)
):
    try:
        if content_type not in ["url", "text", "image"]:
            raise HTTPException(status_code=400, detail="Invalid content type")
        
        if content_type == "image" and image:
            # Upload image to Supabase Storage
            from .storage import save_file_to_storage
            content = await save_file_to_storage(image, uuid)
        elif not content and content_type != "image":
            raise HTTPException(status_code=400, detail="Content is required")
        
        supabase = get_supabase()
        note_data = {
            "uuid": uuid,
            "content_type": content_type,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table('notes').insert(note_data).execute()
        note = response.data[0]
        
        return templates.TemplateResponse(
            "confirmation.html",
            {
                "request": request,
                "content_type": note['content_type'],
                "content": note['content']
            }
        )
    except Exception as e:
        logger.error(f"Error creating note: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    return templates.TemplateResponse(
        "confirmation.html",
        {
            "request": request,
            "content_type": note.content_type,
            "content": note.content
        }
    )