from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import Optional
import logging
from datetime import datetime

from .supabase_client import get_supabase

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI with increased file size limit (15MB)
app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add error handler for 413 Payload Too Large
@app.exception_handler(413)
async def request_entity_too_large(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "File size too large. Maximum size is 15MB."},
        status_code=413
    )

# Add error handler for 500 errors
@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "An internal error occurred"},
        status_code=500
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage - redirect to a default note or show welcome page"""
    import uuid
    # Generate a new UUID for a fresh note
    new_uuid = str(uuid.uuid4())
    return RedirectResponse(url=f"/note/{new_uuid}", status_code=302)

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

@app.put("/note/{uuid}/text")
async def update_text_note(request: Request, uuid: str, content: str = Form(...)):
    """Update the content of a text note. Only text content can be updated."""
    try:
        # Get the current note
        supabase = get_supabase()
        result = supabase.table("notes").select("*").eq("uuid", uuid).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Note not found")
        
        note = result.data[0]
        if note["content_type"] != "text":
            raise HTTPException(status_code=400, detail="Only text notes can be edited")
        
        # Update the note
        result = supabase.table("notes").update({"content": content}).eq("uuid", uuid).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update note")
            
        return RedirectResponse(url=f"/note/{uuid}", status_code=303)
        
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Failed to update note"},
            status_code=500
        )