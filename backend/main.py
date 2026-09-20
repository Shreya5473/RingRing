from datetime import timezone
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reminders", response_model=schemas.ReminderOut)
def create_reminder(data: schemas.ReminderCreate, db: Session = Depends(get_db)):
    due_utc = data.due_at.astimezone(timezone.utc)
    reminder = models.Reminder(
        title=data.title,
        description=data.description,
        due_at=due_utc,
        next_call_at=due_utc,  # first call happens at the deadline time
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@app.get("/reminders", response_model=list[schemas.ReminderOut])
def list_reminders(db: Session = Depends(get_db)):
    query = select(models.Reminder).order_by(models.Reminder.due_at)
    return db.scalars(query).all()


@app.patch("/reminders/{reminder_id}/done", response_model=schemas.ReminderOut)
def mark_done(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.get(models.Reminder, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder.status = "done"
    db.commit()
    db.refresh(reminder)
    return reminder