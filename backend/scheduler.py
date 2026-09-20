from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from database import SessionLocal
import models

RETRY_MINUTES = 30


def process_due_reminders():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        query = select(models.Reminder).where(
            models.Reminder.status == "pending",
            models.Reminder.next_call_at <= now,
        )
        due = db.scalars(query).all()

        for r in due:
            print(f"CALLING: {r.title} (attempt {r.attempts + 1})")
            r.attempts += 1
            if r.attempts >= r.max_attempts:
                r.status = "missed"
            else:
                r.next_call_at = now + timedelta(minutes=RETRY_MINUTES)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    process_due_reminders()