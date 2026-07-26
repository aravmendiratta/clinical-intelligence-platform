from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from uuid import UUID
from sqlalchemy.orm import Session
from ..services.ingestion import enqueue_ingestion
from ..infrastructure.database import get_db, IngestionTask

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/", summary="Upload a document for ingestion")
async def upload_document(file: UploadFile = Depends(), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    task_id = enqueue_ingestion(file, db)
    return JSONResponse(content={"task_id": task_id})

@router.get("/{task_id}", summary="Get ingestion task status")
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task: IngestionTask = db.query(IngestionTask).filter(IngestionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={
        "task_id": task.id,
        "status": task.status,
        "error_message": task.error_message,
    })
