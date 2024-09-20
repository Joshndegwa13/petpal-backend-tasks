from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import crud
from database import SessionLocal, engine
from models import Base
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # Import Uvicorn

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now; adjust based on your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API routes
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(
        description=task.description,
        date=task.date,  # This should handle None values
        completed=task.completed,
        is_daily=task.is_daily
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return tasks

@app.post("/vet_visits/", response_model=schemas.VetVisit)
def create_vet_visit(vet_visit: schemas.VetVisitCreate, db: Session = Depends(get_db)):
    return crud.create_vet_visit(db=db, vet_visit=vet_visit)

@app.get("/vet_visits/", response_model=List[schemas.VetVisit])
def read_vet_visits(db: Session = Depends(get_db)):
    vet_visits = crud.get_vet_visits(db)
    return vet_visits

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, completed: bool, db: Session = Depends(get_db)):
    task = crud.update_task_completion(db, task_id, completed)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks/{task_id}/complete", response_model=schemas.TaskCompletion)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_completion = schemas.TaskCompletionCreate(
        task_id=task_id,
        date=datetime.utcnow()
    )
    return crud.create_task_completion(db, task_completion)

@app.get("/tasks/", response_model=List[schemas.Task])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).options(
        models.Task.completions
    ).all()
    return tasks

@app.get("/tasks/{task_id}/completions", response_model=List[schemas.TaskCompletion])
def get_task_completions(task_id: int, db: Session = Depends(get_db)):
    return crud.get_task_completions(db, task_id)

# Make sure Uvicorn is run when using Vercel
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
